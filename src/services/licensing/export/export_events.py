import structlog

from services.licensing import settings
from services.licensing.business.service import LicensingService
from services.licensing.dynamic_import import dynamic_import

logger = structlog.stdlib.get_logger(__name__)

# export implementations are set in settings (see there)
events_export_pre_export_hook = dynamic_import(settings.events_export_pre_export_hook)
events_export_function = dynamic_import(settings.events_export_function)


async def export_events(max_events: int = 10000) -> None:
    """
    exports event logs as far as there are still not yet exported
    ones in the 'event-log'. This function is called by some
    scheduling mechanism ...
    :param max_events: number of events to export per call
    :return:
    """
    if (
        not settings.events_export_function
        or "do_not_export_event" in settings.events_export_function
    ):
        logger.info("Event log is not being exported (export function not configured)")
        return

    async with settings.transaction_manager() as tm:
        service = LicensingService(settings.repository(tm.session))

        total_events, unexported_events = await service.get_event_log_stats()
        logger.info(
            "Event log export is being executed",
            total_events=total_events,
            unexported_events=unexported_events,
            chunk_size=max_events,
        )

        if unexported_events == 0:
            logger.info("Nothing to export")
            return

        events = await service.get_event_logs(
            is_exported=False, order_by_latest=True, limit=max_events
        )
        for event in events:
            success, type_, timestamp_, payload = await events_export_pre_export_hook(
                event.event_type, event.event_timestamp, event.event_payload
            )
            if not success:
                logger.warn(
                    "Event log modification did not succeed. Will not be exported",
                    event_type=type_,
                    event_payload=payload,
                )
            else:
                if not await events_export_function(type_, timestamp_, payload):
                    logger.warn(
                        "Event export did not succeed for an event",
                        event_type=type_,
                        event_payload=payload,
                    )
                else:
                    await service.update_event_log(event.event_id, is_exported=True)
                    # commit after each row!
                    await tm.commit()
