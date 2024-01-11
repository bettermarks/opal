import datetime
from typing import Tuple


async def no_modification(
    event_type: str, event_timestamp: datetime.datetime, event_payload: dict
) -> Tuple[bool, str, datetime.datetime, dict]:
    """
    Default hook function for event modification before export.
    The default implementation actually does nothing!
    :param event_type: The event type as string
    :param event_timestamp: The event timestamp as datetime object
    :param event_payload: The event payload as dict
    :return: a tuple (success, event_type, event_payload) after modification
    success indicates, if any modification was successful, event_type and
    event_payload are the (modified) event type, event_timestamp, event payload
    """
    return True, event_type, event_timestamp, event_payload


async def do_not_export_event(
    event_type: str, event_timestamp: datetime.datetime, event_payload: dict
) -> bool:
    """
    Default implementation of event export: do nothing
    :param event_type: the event type to export
    :param event_timestamp: the event timestamp to export
    :param event_payload: the event payload to export
    :return: True, if export was successful, False otherwise
    """
    return True
