import datetime
import structlog


logger = structlog.stdlib.get_logger(__name__)


async def export_event(
    event_type: str, event_timestamp: datetime.datetime, event_payload: dict
) -> bool:
    """
    mock implementation of event export: just log
    :param event_type: the event type to export
    :param event_timestamp: the event timestamp to export
    :param event_payload: the event payload to export
    :return: True, if export was successful, False otherwise
    """
    payload = {
        "event_type": event_type,
        "timestamp": str(event_timestamp).split(".")[0],
    } | event_payload
    logger.info(f"Write event with payload {payload} to event service")
    return True
