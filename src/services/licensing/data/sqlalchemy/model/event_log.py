import datetime
from typing import Optional, Dict, Any

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from services.licensing.custom_types import EventLog
from services.licensing.data.sqlalchemy.model.base import Model, UtcNow
from sqlalchemy.dialects.postgresql import JSONB


class EventLogModel(Model):
    __tablename__ = "event_log"

    # columns
    timestamp: Mapped[Optional[datetime.datetime]] = mapped_column(
        server_default=UtcNow(), index=True
    )
    event_type: Mapped[str] = mapped_column(String(256), index=True)
    event_version: Mapped[int] = mapped_column()
    event_payload: Mapped[Dict[str, Any]] = mapped_column(JSONB)
    # just used internally ...
    is_exported: Mapped[bool] = mapped_column(index=True, server_default="false")

    def to_dto(self, with_id=False) -> EventLog:
        return EventLog(
            event_id=self.id if with_id else None,
            event_type=self.event_type,
            event_timestamp=self.timestamp,
            event_version=self.event_version,
            event_payload=self.event_payload,
        )
