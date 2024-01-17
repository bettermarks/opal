import datetime
from typing import Optional

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from services.licensing.data.sqlalchemy.model.base import Model, int8
from services.licensing.custom_types import SeatStatus, Seat


class SeatModel(Model):
    __tablename__ = "seat"

    # columns
    ref_license: Mapped[int8] = mapped_column(ForeignKey("license.id"), index=True)
    user_eid: Mapped[str] = mapped_column(String(256), index=True)
    occupied_at: Mapped[datetime.datetime] = mapped_column(index=True)
    last_accessed_at: Mapped[Optional[datetime.datetime]] = mapped_column(index=True)
    is_occupied: Mapped[bool] = mapped_column(index=True)
    status: Mapped[SeatStatus] = mapped_column(index=True)

    # Relationships
    license: Mapped["LicenseModel"] = relationship(  # noqa: F821
        back_populates="seats", lazy="raise"
    )

    def to_dto(self, with_license=False) -> Seat:
        return Seat(
            id=self.id,
            user_eid=self.user_eid,
            occupied_at=self.occupied_at,
            last_accessed_at=self.last_accessed_at,
            is_occupied=self.is_occupied,
            status=self.status,
            license=self.license.to_dto(with_seats=False) if with_license else None,
        )
