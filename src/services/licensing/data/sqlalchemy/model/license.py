import datetime
import uuid as uuid_module
from typing import List

from sqlalchemy import String, UniqueConstraint, select, func
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from services.licensing.constants import INFINITE_INT_JSON
from services.licensing.custom_types import License
from services.licensing.data.sqlalchemy.model.base import Model, BaseModel
from services.licensing.data.sqlalchemy.model.seat import SeatModel
from services.licensing.utils import nof_free_seats


class LicenseModel(Model):
    __tablename__ = "license"

    uuid: Mapped[uuid_module.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    hierarchy_provider_uri: Mapped[str] = mapped_column(String(256), index=True)
    product_eid: Mapped[str] = mapped_column(String(256), index=True)
    manager_eid: Mapped[str] = mapped_column(String(256), index=True)
    owner_type: Mapped[str] = mapped_column(String(256), index=True)
    owner_level: Mapped[int] = mapped_column(index=True)
    owner_eids: Mapped[List[str]] = mapped_column(ARRAY(String(255)), index=True)
    valid_from: Mapped[datetime.date] = mapped_column(index=True)
    valid_to: Mapped[datetime.date] = mapped_column(index=True)
    nof_seats: Mapped[int]
    extra_seats: Mapped[int]
    order_id: Mapped[str | None] = mapped_column(String(256), index=True)
    is_trial: Mapped[bool] = mapped_column(index=True)
    notes: Mapped[str] = mapped_column(String(4096), nullable=True)

    # Relationships
    # as 'seats' we only list 'occupied' seats, that means
    # all those seats, that are in use ('occupied')
    seats: Mapped[List[SeatModel]] = relationship(
        back_populates="license",
        lazy="raise",
        primaryjoin="and_(LicenseModel.id==SeatModel.ref_license, "
        "SeatModel.is_occupied==True)",
        viewonly=True,
    )
    # as 'released seats', we only list the 'unoccupied' seats, that means
    # all those seats, that are expired or no longer valid because the seat
    # owner has left the license owning entity (class or school etc.)
    released_seats: Mapped[List[SeatModel]] = relationship(
        back_populates="license",
        lazy="raise",
        primaryjoin="and_(LicenseModel.id==SeatModel.ref_license, "
        "SeatModel.is_occupied==False)",
        viewonly=True,
    )

    __table_args__ = (
        UniqueConstraint(
            "product_eid",
            "hierarchy_provider_uri",
            "manager_eid",
            "owner_type",
            "owner_eids",
            "valid_from",
            "valid_to",
        ),
    )

    def to_dto(self, with_seats=True) -> License:
        nof_occupied_seats = len(self.seats) if with_seats else None
        return License(
            id=self.id,
            uuid=self.uuid,
            hierarchy_provider_uri=self.hierarchy_provider_uri,
            product_eid=self.product_eid,
            manager_eid=self.manager_eid,
            owner_type=self.owner_type,
            owner_level=self.owner_level,
            owner_eids=self.owner_eids,
            valid_from=self.valid_from,
            valid_to=self.valid_to,
            nof_seats=self.nof_seats,
            # for API response we ignore extra-seats
            nof_free_seats=(
                nof_free_seats(self.nof_seats, 0, nof_occupied_seats)
                if self.nof_seats != INFINITE_INT_JSON
                else INFINITE_INT_JSON
            ),
            nof_occupied_seats=nof_occupied_seats,
            extra_seats=self.extra_seats,
            is_trial=self.is_trial,
            notes=self.notes,
            seats=[s.to_dto() for s in self.seats] if with_seats else [],
            released_seats=(
                [s.to_dto() for s in self.released_seats] if with_seats else []
            ),
            created_at=self.created_at,
            updated_at=self.updated_at,
        )


class LicensesUnnestedOwnersModel(BaseModel):
    """
    Just a query representing all unnested (by owner) licenses:
    For example, a license with
        id=1 and owner_eids={3,4,5}
    would be transformed to (3 rows)
        id=1, owner_eid=3
        id=1, owner_eid=4
        id=1, owner_eid=5
    """

    unnested = select(
        LicenseModel.id,
        func.unnest(LicenseModel.owner_eids).label("owner_eid"),
    ).subquery()

    __table__ = (
        select(LicenseModel, unnested.c.owner_eid)
        .join(unnested, unnested.c.id == LicenseModel.id)
        .subquery()
    )
