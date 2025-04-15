import datetime

from pydantic import BaseModel


def iso_8601_with_timezone_format(d: datetime.datetime) -> str:
    """
    our preferred datetime format used in the serializers:
    sth. like 2019-11-11T00:52:43.349356+00:00
    """
    return str(d.replace(tzinfo=datetime.timezone.utc).isoformat())


class BaseSchema(BaseModel):
    class Config:
        json_encoders = {datetime.datetime: iso_8601_with_timezone_format}
