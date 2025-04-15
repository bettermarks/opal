import datetime
from freezegun import freeze_time
from fastapi import status


@freeze_time("2023-01-01")
async def test_export_event_do_nothing():
    from services.licensing.export.bettermarks_export import export_event

    assert (
        await export_event("DummyType", datetime.datetime.now(), {"a": "test"}) is True
    )


async def test_export_event_http_exception(mocker):
    from services.licensing.export.bettermarks_export import export_event
    from services.licensing.exceptions import HTTPException

    mocker.patch("services.licensing.settings.bm_data_event_api_url", "anything")
    mocker.patch(
        "services.licensing.export.bettermarks_export.post_request",
        side_effect=HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, message="MockedError"
        ),
    )
    assert (
        await export_event("DummyType", datetime.datetime.now(), {"a": "test"}) is False
    )
