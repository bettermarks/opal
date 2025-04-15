import datetime
from typing import List, Tuple, Dict, Any

from fastapi import status as http_status
from sqlalchemy import (
    select,
    tuple_,
    update,
    text,
    Select,
    or_,
    func,
    false,
    and_,
    true,
    case,
    distinct,
    delete,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from services.licensing.custom_types import (
    Seat,
    License,
    Entity,
    OrderByDirection,
    EventLog,
    EventType,
    SeatStatus,
)
from services.licensing.data.repository import LicensingRepository
from services.licensing.data.sqlalchemy.model.event_log import EventLogModel
from services.licensing.data.sqlalchemy.model.license import (
    LicenseModel,
    LicensesUnnestedOwnersModel,
)
from services.licensing.data.sqlalchemy.model.seat import SeatModel
from services.licensing.data.sqlalchemy.pagination import execute_paginated_query
from services.licensing.exceptions import HTTPException


def apply_filter_restrictions(
    query: Select,
    filter_restrictions: Dict[str, List[str]],
    allowed_filter_restrictions: List[str],
):
    """
    We have introduced some additional security mechanism for admin routes
    (/licenses, /licenses{license_id}) using a 'filter_restrictions' dict
    in the 'admin token'. This is something like:

    {"manager_eid": ["DE_bettermarks", "DE_test"]}

    This function interprets the 'filter restrictions' like so: A given license
    passes the function with 'True' in the example case above, if and only if
    it has a 'manager_eid' like '*DE_bettermarks*' OR '*DE_test*'.
    :param query: the query to apply the filters to
    :param filter_restrictions: see above
    :param allowed_filter_restrictions: list of allowed filter restrictions to apply
    :return: the modified query
    :raise: HttpException, if filter_restrictions is malformed or not allowed
    """
    filtered_query = query
    for f_key, f_values in filter_restrictions.items():
        # only lists allowed ...
        if not isinstance(f_values, list) or f_key not in allowed_filter_restrictions:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                message=(
                    "'filter_restrictions' in given admin token is either malformed or "
                    "contains not allowed filter keys"
                ),
                filter_restrictions=filter_restrictions,
            )
        filtered_query = filtered_query.where(
            or_(
                *[
                    getattr(LicenseModel, f_key).contains(f_value)
                    for f_value in f_values
                ]
            )
        )
    return filtered_query


class LicensingRepositorySqlalchemyImpl(LicensingRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def is_db_alive(self) -> bool:
        try:
            await self.session.execute(text("SELECT 1"))
            return True
        except Exception:
            return False

    async def create_license(self, **data) -> None:
        self.session.add(LicenseModel(**data))

    async def create_seat(self, **data) -> None:
        self.session.add(SeatModel(**{k: v for k, v in data.items() if k != "uuid"}))

    async def delete_license(self, license_uuid: str) -> None:
        await self.session.execute(
            delete(LicenseModel).where(LicenseModel.uuid == license_uuid)
        )

    async def update_license(
        self, license_uuid: str, license_filter_restrictions: Any, **data
    ) -> License:
        l_ = (
            await self.session.scalars(
                update(LicenseModel)
                .where(LicenseModel.uuid == license_uuid)
                .values(**data)
                .options(selectinload(LicenseModel.seats))
                .options(selectinload(LicenseModel.released_seats))
                .returning(LicenseModel)
            )
        ).one_or_none()
        return l_.to_dto()

    async def update_seats(self, seats: List[Seat]) -> None:
        await self.session.execute(
            update(SeatModel),
            [
                {
                    "id": s_.id,
                    "user_eid": s_.user_eid,
                    "occupied_at": s_.occupied_at,
                    "last_accessed_at": s_.last_accessed_at,
                    "is_occupied": s_.is_occupied,
                    "status": s_.status,
                }
                for s_ in seats
            ],
        )

        for s_ in seats:
            if s_.status != SeatStatus.ACTIVE:
                await self.create_event_log(
                    EventType.SEAT_UPDATED,
                    {
                        "uuid": s_.license.uuid,
                        "user_eid": s_.user_eid,
                        "occupied_at": s_.occupied_at,
                        "last_accessed_at": s_.last_accessed_at,
                        "is_occupied": s_.is_occupied,
                        "status": s_.status,
                    },
                )

    async def get_managed_licenses_paginated(
        self,
        page: int,
        page_size: int,
        order_by_fields: List[Tuple[str, str]],
        hierarchy_provider_uri: str,
        user_eid: str,
    ) -> Tuple[List[License], int]:
        items, total = await execute_paginated_query(
            self.session,
            select(LicenseModel)
            .where(
                LicenseModel.hierarchy_provider_uri == hierarchy_provider_uri,
                LicenseModel.manager_eid == user_eid,
            )
            .options(selectinload(LicenseModel.seats))
            .options(selectinload(LicenseModel.released_seats))
            .order_by(
                *[
                    (
                        getattr(LicenseModel, field).desc()
                        if dir_ == OrderByDirection.DESC
                        else getattr(LicenseModel, field)
                    )
                    for field, dir_ in order_by_fields
                ]
            ),
            page,
            page_size,
        )
        return [l_.to_dto() for l_ in items], total

    async def get_managed_licenses_by_id(
        self,
        license_id: str,
        hierarchy_provider_uri: str,
        user_eid: str,
    ) -> License:
        license_item_stmt = (
            select(LicenseModel)
            .where(
                LicenseModel.uuid == license_id,
                LicenseModel.hierarchy_provider_uri == hierarchy_provider_uri,
                LicenseModel.manager_eid == user_eid,
            )
            .options(
                selectinload(LicenseModel.seats),
                selectinload(LicenseModel.released_seats),
            )
        )
        result = await self.session.execute(license_item_stmt)
        license_item = result.scalar()
        return license_item.to_dto() if license_item else None

    async def get_licenses_for_entities_paginated(
        self,
        page: int,
        page_size: int,
        order_by_fields: List[Tuple[str, str]],
        hierarchy_provider_uri: str,
        entities: List[Entity],
    ) -> Tuple[List[License], int]:
        # subquery for all license ids with owners unnested to rows ...
        subquery_licenses = (
            select(LicensesUnnestedOwnersModel.id)
            .where(
                LicensesUnnestedOwnersModel.hierarchy_provider_uri
                == hierarchy_provider_uri,
                tuple_(
                    LicensesUnnestedOwnersModel.owner_type,
                    LicensesUnnestedOwnersModel.owner_eid,
                ).in_([(e_.type_, e_.eid) for e_ in entities]),
            )
            .distinct()
        ).subquery()

        stmt = (
            select(LicenseModel)
            .join(subquery_licenses, subquery_licenses.c.id == LicenseModel.id)
            .options(selectinload(LicenseModel.seats))
            .options(selectinload(LicenseModel.released_seats))
            .order_by(
                *[
                    (
                        getattr(LicenseModel, field).desc()
                        if dir_ == OrderByDirection.DESC
                        else getattr(LicenseModel, field)
                    )
                    for field, dir_ in order_by_fields
                ]
            )
        )

        items, total = await execute_paginated_query(
            self.session,
            stmt,
            page,
            page_size,
        )
        return [l_.to_dto() for l_ in items], total

    async def get_licenses_paginated(
        self,
        page: int,
        page_size: int,
        order_by_fields: List[Tuple[str, str]],
        filter_restrictions: Dict[str, List[str]],
        allowed_filter_restrictions: List[str],
        **filters,
    ) -> Tuple[List[License], int]:
        """
        helper: gets all licenses, paginated, with order by and filters
        :returns: a tuple with
            (a list of License DTO objects, the total number of licenses)
        """
        date_now = datetime.datetime.now(tz=datetime.timezone.utc)
        filter_is_valid = filters.get("is_valid")
        stmt = (
            select(LicenseModel)
            .join(
                LicensesUnnestedOwnersModel,
                LicensesUnnestedOwnersModel.id == LicenseModel.id,
            )
            .where(
                (
                    LicenseModel.product_eid.contains(filters["product_eid"])
                    if filters.get("product_eid")
                    else text("")
                ),
                (
                    LicenseModel.owner_type == filters["owner_type"]
                    if filters.get("owner_type")
                    else text("")
                ),
                (
                    LicenseModel.owner_level == filters["owner_level"]
                    if filters.get("owner_level")
                    else text("")
                ),
                (
                    LicensesUnnestedOwnersModel.owner_eid.contains(filters["owner_eid"])
                    if filters.get("owner_eid")
                    else text("")
                ),
                (
                    LicenseModel.manager_eid.contains(filters["manager_eid"])
                    if filters.get("manager_eid")
                    else text("")
                ),
                (
                    LicenseModel.valid_from >= filters["valid_from"]
                    if filters.get("valid_from")
                    else text("")
                ),
                (
                    LicenseModel.valid_to <= filters["valid_to"]
                    if filters.get("valid_to")
                    else text("")
                ),
                (
                    LicenseModel.is_trial.is_(filters["is_trial"])
                    if filters.get("is_trial") is not None
                    else text("")
                ),
                (
                    LicenseModel.created_at >= filters["created_at"]
                    if filters.get("created_at")
                    else text("")
                ),
                # filter by `is_valid`
                (
                    LicenseModel.valid_from <= date_now
                    if filter_is_valid is True
                    else (
                        LicenseModel.valid_from > date_now
                        if filter_is_valid is False
                        else text("")
                    )
                ),
                (
                    LicenseModel.valid_to >= date_now
                    if filter_is_valid is True
                    else (
                        LicenseModel.valid_to < date_now
                        if filter_is_valid is False
                        else text("")
                    )
                ),
            )
            .options(selectinload(LicenseModel.seats))
            .options(selectinload(LicenseModel.released_seats))
            .order_by(
                *[
                    (
                        getattr(LicenseModel, field).desc()
                        if dir == OrderByDirection.DESC
                        else getattr(LicenseModel, field)
                    )
                    for field, dir in order_by_fields
                ]
            )
        )
        #
        # special aggregation filters:
        #
        if filters.get("redeemed_seats"):
            # Filter uses the following logic in `having` clause:
            # - number of redeemed seats * 1/10000000000  >= 80% (or something)
            # [if nof_seats is infinity (NEVER TRUE)]
            # - number of redeemed seats * 10000000000  >= 80% (or something)
            # [if nof_seats is 0 (ALWAYS TRUE)]
            # - number of redeemed seats * 1.0/nof_seats  >= 80% (or something)
            # [true if, redeemed seats / nof_seats >= 0.8 etc. (The usual case)]
            stmt = (
                stmt.join(
                    SeatModel,
                    and_(
                        SeatModel.ref_license == LicenseModel.id,
                        SeatModel.is_occupied == true(),
                    ),
                    isouter=True,
                )
                .group_by(LicenseModel.id)
                .having(
                    1.0
                    # distinct is important here to reflect the possibility of
                    # multiple owner eids per license. Otherwise, the count
                    # would be multiplied by the number of owner eids!
                    * func.count(distinct(SeatModel.id))
                    * case(
                        (LicenseModel.nof_seats <= -1, 1.0 / 10000000000),
                        (LicenseModel.nof_seats <= 0, 10000000000),
                        else_=1.0 / LicenseModel.nof_seats,
                    )
                    >= filters["redeemed_seats"] / 100.0
                )
            )
        stmt = stmt.distinct()

        items, total = await execute_paginated_query(
            self.session,
            apply_filter_restrictions(
                stmt, filter_restrictions, allowed_filter_restrictions
            ),
            page,
            page_size,
        )

        return [l_.to_dto() for l_ in items], total

    async def get_license(
        self,
        license_uuid: str,
        filter_restrictions: Dict[str, List[str]],
        allowed_filter_restrictions: List[str],
    ) -> License | None:
        """
        helper: gets all details for a given license ID
        :returns: a License DTO or None
        """
        stmt = (
            select(LicenseModel)
            .where(LicenseModel.uuid == license_uuid)
            .options(selectinload(LicenseModel.seats))
            .options(selectinload(LicenseModel.released_seats))
        )
        license_ = (
            (
                await self.session.execute(
                    apply_filter_restrictions(
                        stmt, filter_restrictions, allowed_filter_restrictions
                    )
                )
            )
            .scalars()
            .first()
        )
        return license_.to_dto() if license_ else None

    async def get_valid_licenses_for_entities(
        self,
        hierarchy_provider_uri: str,
        entities: List[Entity],
        when: datetime.date,
    ) -> List[License]:
        """
        helper: gets all (distinct) licenses, that are valid at a given date (when),
        that are owned by the given entities under a given hierarchy provider.
        :returns: a list of License DTO objects
        """
        # query for all license ids, that are currently valid ...
        valid_licenses = (
            select(LicensesUnnestedOwnersModel.id)
            .where(
                LicensesUnnestedOwnersModel.hierarchy_provider_uri
                == hierarchy_provider_uri,
                LicensesUnnestedOwnersModel.valid_from <= when,
                LicensesUnnestedOwnersModel.valid_to >= when,
                tuple_(
                    LicensesUnnestedOwnersModel.owner_type,
                    LicensesUnnestedOwnersModel.owner_eid,
                ).in_([(e_.type_, e_.eid) for e_ in entities]),
            )
            .distinct()
        ).subquery()

        return [
            l_.to_dto()
            for l_ in (
                (
                    await self.session.execute(
                        select(LicenseModel)
                        .join(valid_licenses, valid_licenses.c.id == LicenseModel.id)
                        .options(selectinload(LicenseModel.seats))
                        .options(selectinload(LicenseModel.released_seats))
                    )
                )
                .scalars()
                .all()
            )
        ]

    async def get_occupied_seats(self, user_eid: str) -> List[Seat]:
        """
        Gets all seats, that are currently 'occupied'
        :param user_eid: the EID of the requesting user
        :return: a list of dicts representing 'seats' with their licenses!.
        """
        occupied_seats = (
            (
                await self.session.execute(
                    select(SeatModel)
                    .where(SeatModel.user_eid == user_eid, SeatModel.is_occupied)
                    .options(
                        # explict eager loading as async doesn't support lazy loading
                        selectinload(SeatModel.license)
                    )
                )
            )
            .scalars()
            .all()
        )
        return [s_.to_dto(with_license=True) for s_ in occupied_seats]

    async def create_event_log(
        self,
        type_: EventType,
        payload: Dict[str, Any],
        version: int = 1,
        is_exported: bool = False,
    ):
        self.session.add(
            EventLogModel(
                event_type=type_.value,
                timestamp=datetime.datetime.now(tz=datetime.timezone.utc),
                event_version=version,
                event_payload=payload,
                is_exported=is_exported,
            )
        )

    async def get_event_log_stats(self) -> Tuple[int, int]:
        result = (
            await self.session.execute(
                select(
                    func.count().label("total"),
                    func.count()
                    .filter(EventLogModel.is_exported == false())
                    .label("unexported"),
                ).select_from(EventLogModel)
            )
        ).one()
        return result.total, result.unexported

    async def get_event_logs(
        self, is_exported=False, order_by_latest=False, limit=1000000
    ) -> List[EventLog]:
        event_logs = (
            (
                await self.session.execute(
                    select(EventLogModel)
                    .where(EventLogModel.is_exported == is_exported)
                    .order_by(
                        EventLogModel.id.desc()
                        if order_by_latest
                        else EventLogModel.id.asc()
                    )
                    .limit(limit)
                )
            )
            .scalars()
            .all()
        )
        return [e_.to_dto(with_id=True) for e_ in event_logs]

    async def update_event_log(self, event_log_id: int, **data) -> None:
        await self.session.execute(
            update(EventLogModel).where(EventLogModel.id == event_log_id).values(**data)
        )
