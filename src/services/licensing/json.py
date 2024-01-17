import datetime
import json
from uuid import UUID

from services.licensing.custom_types import SeatStatus


class CustomJSONEncoder(json.JSONEncoder):
    """
    a slightly modified JSON encoder supporting UUIDs and other custom types
    """

    def default(self, obj):
        if isinstance(obj, datetime.date):
            return obj.isoformat()
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        if isinstance(obj, UUID):
            return str(obj)
        if isinstance(obj, SeatStatus):
            return str(obj)
        return super().default(obj)


def custom_json_dumps(obj, **kwargs):
    return json.dumps(obj, cls=CustomJSONEncoder, **kwargs)
