import datetime

from pydantic import BaseModel as BaseSchema, Field

from services.licensing.custom_types import SeatStatus


class SeatBaseSchema(BaseSchema):
    user_eid: str = Field(min_length=1, max_length=256)


class SeatCreateSchema(SeatBaseSchema):
    pass


class SeatSchema(SeatBaseSchema):
    occupied_at: datetime.datetime
    last_accessed_at: datetime.datetime
    is_occupied: bool
    status: SeatStatus

    class Config:
        from_attributes = True
