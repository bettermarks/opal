import datetime
import uuid as uuid_module
from functools import reduce
from typing import List, Dict, Tuple

from services.licensing.data.repository import LicensingRepository
from services.licensing.custom_types import (
    SeatStatus,
    Memberships,
    Hierarchies,
    Entity,
    License,
    EventLog,
    EventType,
)
from services.licensing.hierarchies import get_ancestors
from services.licensing.utils import nof_free_seats


class LicensingService:
    """
    Concrete implementation of the business logic
    """

    def __init__(self, licensing_repository: LicensingRepository):
        self.licensing_repository = licensing_repository

    async def is_db_alive(self) -> bool:
        return await self.licensing_repository.is_db_alive()

    async def delete_license(self, license_uuid: str) -> None:
        await self.licensing_repository.delete_license(license_uuid)

    async def create_license(self, **license_data) -> Dict[str, str]:
        data = license_data.copy()
        if "uuid" not in data:
            data["uuid"] = uuid_module.uuid4()
        # extra_seats falls back to 0 if None
        data["extra_seats"] = data["extra_seats"] or 0
        # nof_seats falls back to infinity (-1) if None
        if data["nof_seats"] is None:
            data["nof_seats"] = -1
        await self.licensing_repository.create_license(**data)
        await self.licensing_repository.create_event_log(
            EventType.LICENSE_CREATED, data
        )
        return {
            "uuid": data["uuid"],
            "product_eid": data["product_eid"],
            "valid_from": data["valid_from"],
            "valid_to": data["valid_to"],
            "owner_level": data["owner_level"],
            "owner_type": data["owner_type"],
            "nof_seats": data["nof_seats"],
            "nof_free_seats": data["nof_seats"],
            "nof_occupied_seats": 0,
            "extra_seats": data["extra_seats"],
            "is_trial": data["is_trial"],
        }

    async def create_seat(self, **seat_data) -> None:
        await self.licensing_repository.create_seat(**seat_data)
        await self.licensing_repository.create_event_log(
            EventType.SEAT_CREATED,
            {k: v for k, v in seat_data.items() if k != "ref_license"},
        )

    async def update_license(
        self, license_uuid: str, license_filter_restrictions=None, **license_data
    ) -> License:
        """
        License object update method.

        :param license_uuid: license number (uuid)
        :param license_filter_restrictions:
        :returns the just update license (DTO object)
        """
        data = license_data.copy()
        # extra_seats falls back to 0 if None
        if "extra_seats" in data:
            data["extra_seats"] = data["extra_seats"] or 0
        # nof_seats falls back to infinity (-1) if None
        if "nof_seats" in data and data["nof_seats"] is None:
            data["nof_seats"] = -1
        l_ = await self.licensing_repository.update_license(
            license_uuid=license_uuid,
            license_filter_restrictions=license_filter_restrictions,
            **data
        )
        await self.licensing_repository.create_event_log(
            EventType.LICENSE_UPDATED,
            {"uuid": license_uuid, "manager_eid": l_.manager_eid} | data,
        )
        return l_

    async def get_accessible_products(
        self, hierarchy_provider_uri: str, user_eid: str, memberships: Memberships
    ) -> List[str]:
        """
        A just logged-in user (student or teacher) wants to get his accessable
        products.

        The seat occupying algorithm works as follows:
        1. Get all 'seats' (with attached licenses), the user already has
           'occupied'. We call the licenses that already 'have a seat occupied',
           'occupied licenses'.
           1.b: Check seats and maybe update the state of the seat like so:
               - if the license attached to a seat has been expired, state of
                 the seat gets 'EXPIRED'.
               - if the memberships of a requesting user are disjoint with the
                 owners of the seat attached license, the state of the seats
                 gets 'NOT-A-MEMBER'.
               In every case described above, the product attached to the license
               that is attached to the 'no longer valid' seat, is no longer available
               to the user. Every seat matching the criteria above will be removed
               from the 'occupied seats' list.
        2. Extract all products from the 'occupied licenses'. We call those
           products 'occupied products'.
        3. Get all licenses, that apply to the requesting users (by membership)
            and that are still valid (per today).
        4. Filter OUT those licenses, that
             a. no longer have free seats.
             b. have products attached, that have already been seen as
                'occupied products'.
           We will call the products that result from this list
           'unoccupied products'. After filtering, we will sort those filtered
           licenses by ('product','owner level', 'free seats'). We will call that
           list 'filtered and sorted valid licenses'.
        5. A seat will be occupied for the FIRST license for EACH product in the
           'filtered and sorted valid licenses' list. We will call those licenses
           'licenses to occupy'.
        6. Return the EIDs merged from 'occupied products' and 'unoccupied products'

        :param hierarchy_provider_uri: the URI of the hierarchy provider
        :param user_eid: the user EID
        :param memberships: memberships structure
        :returns all the product EIDs gotten from the licenses
        :raises HTTPException: possible codes 400, 401, 409, 422
        """
        now = datetime.datetime.now(tz=datetime.timezone.utc)

        # 1. get all seats 'occupied' by the requesting user
        occupied_seats = await self.licensing_repository.get_occupied_seats(user_eid)

        # 1.b seats will also be updated ...
        occupied_seats_to_remove = []

        for seat in occupied_seats:
            # update 'last_accessed_at' in any case!
            seat.last_accessed_at = now

            # has the attached license expired?
            if seat.license.valid_to < now.date():
                occupied_seats_to_remove.append(seat)
                seat.status = SeatStatus.EXPIRED
                seat.is_occupied = False
                continue

            # is the memberships disjoint with the owners?
            owners = {
                Entity(type_=seat.license.owner_type, eid=o_eid)
                for o_eid in seat.license.owner_eids
            }
            members = {k for k in memberships}
            if not owners.intersection(members):
                occupied_seats_to_remove.append(seat)
                seat.status = SeatStatus.NOT_A_MEMBER
                seat.is_occupied = False

        # 1.b.1 ok, update the seats in the data layer
        await self.licensing_repository.update_seats(occupied_seats)

        # 1.b.2 .. and remove the seats from the occupied seats list
        for seat in occupied_seats_to_remove:
            occupied_seats.remove(seat)

        # 2. extract unique 'occupied products'.
        occupied_product_eids = list(
            {seat.license.product_eid for seat in occupied_seats}
        )

        # 3. get all the 'valid licenses'
        valid_licenses = (
            await self.licensing_repository.get_valid_licenses_for_entities(
                hierarchy_provider_uri,
                memberships,
                now.date(),
            )
        )

        # 4. apply the filters and sorting mentioned above
        filtered_and_sorted_valid_licenses = sorted(
            filter(
                lambda l_: nof_free_seats(l_.nof_seats, l_.extra_seats, len(l_.seats))
                > 0
                and l_.product_eid not in occupied_product_eids,
                valid_licenses,
            ),
            # sort by 'product' and 'owner level' and free seats desc. (step 3)
            key=lambda l_: (
                l_.product_eid,
                l_.owner_level,
                -1 * nof_free_seats(l_.nof_seats, l_.extra_seats, len(l_.seats)),
            ),
        )

        # 5. ok, create a new list, in which only the first elements for every
        # distinct product eid are inserted. This gives a list of all licenses,
        # where all possible products are available ...
        licenses_to_occupy = reduce(
            lambda acc, l_: (
                acc + [l_] if not acc or acc[-1].product_eid != l_.product_eid else acc
            ),
            filtered_and_sorted_valid_licenses,
            [],
        )
        # occupy the seats
        for _l in licenses_to_occupy:
            await self.create_seat(
                user_eid=user_eid,
                occupied_at=now,
                last_accessed_at=now,
                is_occupied=True,
                status=SeatStatus.ACTIVE,
                ref_license=_l.id,
                uuid=_l.uuid,  # uuid will only be used to build up events
            )

        # 6.  merge the relevant products
        accessible_products = occupied_product_eids + [
            l_.product_eid for l_ in licenses_to_occupy
        ]

        await self.licensing_repository.create_event_log(
            EventType.PERMISSIONS_REQUESTED,
            {
                "hierarchy_provider_uri": hierarchy_provider_uri,
                "user_eid": user_eid,
                "accessible_products": accessible_products,
            },
        )
        return accessible_products

    async def get_valid_licenses_for_entity_tree(
        self,
        hierarchy_provider_uri: str,
        entity_type: str,
        entity_eid: str,
        hierarchies: Hierarchies,
    ) -> List[License]:
        """
        gets all valid licenses for a given entity in a hierarchy structure.
        The 'valid licenses for an entity' are defined by 'all licenses, that
        are currently not expired and that still have free seats available and
        that are owned by some ancestor of a given entity or by the entity
        itself'.
        :param hierarchy_provider_uri:
        :param entity_type: the entity type
        :param entity_eid: the entity eid to get the valid licenses for
        :param hierarchies: a hierarchies structure
        :return: all valid licenses for an entity
        """
        ancestors = get_ancestors(entity_type, entity_eid, hierarchies)
        licenses = await self.licensing_repository.get_valid_licenses_for_entities(
            hierarchy_provider_uri,
            ancestors + [Entity(type_=entity_type, eid=entity_eid)],
            datetime.date.today(),
        )
        # check for free seats!
        return list(
            filter(
                lambda l_: nof_free_seats(l_.nof_seats, l_.extra_seats, len(l_.seats))
                > 0,
                licenses,
            )
        )

    async def get_active_license_for_entity_tree(
        self,
        hierarchy_provider_uri: str,
        entity_type: str,
        entity_eid: str,
        hierarchies: Hierarchies,
    ) -> License | None:
        """
        the 'active license' for a given entity, that is the license taken
        from the set of 'valid' licenses (see above route
        'entity_type}/{entity_eid}/valid-licenses'), that has the
        - minimum owner level
        - (for same owner level) maximum number of free seats
        :param hierarchy_provider_uri:
        :param entity_type: the entity type
        :param entity_eid: the entity eid to get the valid licenses for
        :param hierarchies: a hierarchies structure
        :return: the active entity for an entity (or None)
        """
        sorted_valid_licenses = sorted(
            await self.get_valid_licenses_for_entity_tree(
                hierarchy_provider_uri, entity_type, entity_eid, hierarchies
            ),
            key=lambda l_: (
                l_.owner_level,
                -1 * nof_free_seats(l_.nof_seats, l_.extra_seats, len(l_.seats)),
            ),
        )
        return sorted_valid_licenses[0] if sorted_valid_licenses else None

    async def get_valid_licenses_for_entity(
        self, hierarchy_provider_uri, entity_type, entity_eid
    ) -> List[License]:
        """
        gets all valid and directly attached licenses for a given entity.
        The 'valid licenses for an entity' are defined by 'all licenses, that
        are currently not expired and that still have free seats available and
        that are owned by the entity itself'.
        :param hierarchy_provider_uri:
        :param entity_type: the entity type
        :param entity_eid: the entity eid to get the valid licenses for
        :return: all valid licenses for an entity
        """
        licenses = await self.licensing_repository.get_valid_licenses_for_entities(
            hierarchy_provider_uri,
            [Entity(type_=entity_type, eid=entity_eid)],
            datetime.date.today(),
        )
        # check for free seats!
        return list(
            filter(
                lambda l_: nof_free_seats(l_.nof_seats, l_.extra_seats, len(l_.seats))
                > 0,
                licenses,
            )
        )

    async def get_managed_licenses_paginated(
        self,
        page: int,
        page_size: int,
        order_by_fields: List[Tuple[str, str]],
        hierarchy_provider_uri: str,
        user_eid: str,
    ) -> List[License]:
        return await self.licensing_repository.get_managed_licenses_paginated(
            page, page_size, order_by_fields, hierarchy_provider_uri, user_eid
        )

    async def get_managed_licenses_by_id(
        self,
        license_id: str,
        hierarchy_provider_uri: str,
        user_eid: str,
    ) -> License:
        return await self.licensing_repository.get_managed_licenses_by_id(
            license_id, hierarchy_provider_uri, user_eid
        )

    async def get_licenses_for_entities_paginated(
        self,
        page: int,
        page_size: int,
        order_by_fields: List[Tuple[str, str]],
        hierarchy_provider_uri: str,
        entities: List[Entity],
    ) -> Tuple[List[License], int]:
        return await self.licensing_repository.get_licenses_for_entities_paginated(
            page, page_size, order_by_fields, hierarchy_provider_uri, entities
        )

    async def get_licenses_paginated(
        self,
        page: int,
        page_size: int,
        order_by_fields: List[Tuple[str, str]],
        filter_restrictions: Dict[str, List[str]],
        allowed_filter_restrictions: List[str],
        **filters
    ) -> Tuple[List[License], int]:
        return await self.licensing_repository.get_licenses_paginated(
            page,
            page_size,
            order_by_fields,
            filter_restrictions,
            allowed_filter_restrictions,
            **filters
        )

    async def get_license(
        self,
        license_uuid: str,
        filter_restrictions: Dict[str, List[str]],
        allowed_filter_restrictions: List[str],
    ) -> License:
        return await self.licensing_repository.get_license(
            license_uuid, filter_restrictions, allowed_filter_restrictions
        )

    async def get_event_log_stats(self) -> Tuple[int, int]:
        return await self.licensing_repository.get_event_log_stats()

    async def get_event_logs(
        self, is_exported=False, order_by_latest=False, limit=1000000
    ) -> List[EventLog]:
        return await self.licensing_repository.get_event_logs(
            is_exported=is_exported, order_by_latest=order_by_latest, limit=limit
        )

    async def update_event_log(self, event_log_id: int, **data):
        await self.licensing_repository.update_event_log(
            event_log_id=event_log_id, **data
        )
