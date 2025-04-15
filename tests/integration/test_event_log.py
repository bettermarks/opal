import datetime
import json
from copy import deepcopy
from dataclasses import asdict

from httpx import AsyncClient
from fastapi import status as http_status
from freezegun import freeze_time

import pytest

from services.licensing.custom_types import SeatStatus, EventType
from tests.integration.conftest import query_event_log


#
# redeeming tests
#


def dict_without_event_id(data):
    return {key: value for key, value in data if key != "event_id"}


@pytest.mark.asyncio
@freeze_time("2023-01-01")
async def test_event_log_purchase_license__ok(
    client: AsyncClient,
    teacher_1,
    teacher_1_shop_authorization_token,
    teacher_1_purchase_payload,
):
    response = await client.post(
        "/v1/order/licenses",
        json={},
        headers={"Authorization": f"Bearer {teacher_1_shop_authorization_token}"},
    )
    assert response.status_code == http_status.HTTP_201_CREATED
    result_json = json.loads(response._content)

    assert [
        asdict(l_, dict_factory=dict_without_event_id) for l_ in await query_event_log()
    ] == [
        {
            "event_type": str(EventType.LICENSE_CREATED),
            "event_timestamp": datetime.datetime(
                2023, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc
            ),
            "event_version": 1,
            "event_payload": {
                "uuid": result_json["uuid"],
                "is_trial": False,
                "valid_from": teacher_1_purchase_payload["valid_from"],
                "valid_to": teacher_1_purchase_payload["valid_to"],
                "nof_seats": teacher_1_purchase_payload["nof_seats"],
                "extra_seats": teacher_1_purchase_payload["extra_seats"],
                "owner_eids": teacher_1_purchase_payload["owner_eids"],
                "owner_type": teacher_1_purchase_payload["owner_type"],
                "manager_eid": teacher_1.eid,
                "owner_level": teacher_1_purchase_payload["owner_level"],
                "product_eid": teacher_1_purchase_payload["product_eid"],
                "hierarchy_provider_uri": teacher_1_purchase_payload[
                    "hierarchy_provider_uri"
                ],
                "order_id": None,
            },
        }
    ]


@pytest.mark.asyncio
@freeze_time("2023-01-01")
async def test_event_log_create_trial_license__ok(
    client: AsyncClient,
    teacher_1,
    teacher_1_memberships,
    teacher_1_memberships_authorization_token,
    teacher_1_trial_payload,
    hierarchy_provider_1_uri,
):
    payload = deepcopy(teacher_1_trial_payload)
    payload["memberships"] = teacher_1_memberships

    response = await client.post(
        "/v1/member/licenses/trial",
        json=payload,
        headers={
            "Authorization": f"Bearer {teacher_1_memberships_authorization_token}"
        },
    )
    assert response.status_code == http_status.HTTP_201_CREATED
    result_json = json.loads(response._content)

    assert [
        asdict(l_, dict_factory=dict_without_event_id) for l_ in await query_event_log()
    ] == [
        {
            "event_type": str(EventType.LICENSE_CREATED),
            "event_timestamp": datetime.datetime(
                2023, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc
            ),
            "event_version": 1,
            "event_payload": {
                "uuid": result_json["uuid"],
                "is_trial": True,
                "valid_from": "2023-01-01",
                "valid_to": "2023-02-26",
                "nof_seats": 50,
                "extra_seats": 0,
                "owner_eids": [teacher_1_trial_payload["owner_eid"]],
                "owner_type": teacher_1_trial_payload["owner_type"],
                "manager_eid": teacher_1.eid,
                "owner_level": teacher_1_trial_payload["owner_level"],
                "product_eid": teacher_1_trial_payload["product_eid"],
                "hierarchy_provider_uri": hierarchy_provider_1_uri,
            },
        }
    ]


@pytest.mark.asyncio
@freeze_time("2023-01-01")
async def test_event_log_update_license__ok(
    client: AsyncClient,
    teacher_1,
    teacher_1_memberships,
    teacher_1_memberships_authorization_token,
    teacher_1_trial_payload,
    create_license,
    update_license,
):
    license_uuid = "22222222-aea8-4de2-bcca-7b1945285502"
    await create_license(
        uuid=license_uuid,
        valid_from=datetime.date(2000, 1, 1),
        valid_to=datetime.date(2023, 1, 1),
    )
    l_ = await update_license(license_uuid, valid_to=datetime.date(2023, 12, 31))
    assert str(l_.uuid) == license_uuid
    assert [
        asdict(l_, dict_factory=dict_without_event_id)
        for l_ in (await query_event_log())[1:]
    ] == [
        {
            "event_type": str(EventType.LICENSE_UPDATED),
            "event_timestamp": datetime.datetime(
                2023, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc
            ),
            "event_version": 1,
            "event_payload": {
                "uuid": license_uuid,
                "valid_to": "2023-12-31",
                "manager_eid": teacher_1.eid,
            },
        }
    ]


@pytest.mark.asyncio
@freeze_time("2023-01-01")
async def test_event_log_redeem_license__ok(
    client: AsyncClient,
    create_license,
    student_1_class_1_memberships,
    student_1_class_1_memberships_authorization_token,
    student_1,
    hierarchy_provider_1_uri,
    product_1_eid,
):
    # in this case, no event log for creating licens is being created
    uuid = "22222222-aea8-4de2-bcca-7b1945285502"
    await create_license(uuid=uuid)

    response = await client.post(
        "/v1/member/permissions",
        json={"memberships": student_1_class_1_memberships},
        headers={
            "Authorization": f"Bearer {student_1_class_1_memberships_authorization_token}"
        },
    )
    assert response.status_code == http_status.HTTP_200_OK
    assert [
        asdict(l_, dict_factory=dict_without_event_id)
        for l_ in (await query_event_log())[1:]
    ] == [
        {
            "event_type": str(EventType.SEAT_CREATED),
            "event_timestamp": datetime.datetime(
                2023, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc
            ),
            "event_version": 1,
            "event_payload": {
                "uuid": uuid,
                "status": str(SeatStatus.ACTIVE),
                "user_eid": student_1.eid,
                "is_occupied": True,
                "occupied_at": "2023-01-01T00:00:00+00:00",
                "last_accessed_at": "2023-01-01T00:00:00+00:00",
            },
        },
        {
            "event_type": str(EventType.PERMISSIONS_REQUESTED),
            "event_timestamp": datetime.datetime(
                2023, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc
            ),
            "event_version": 1,
            "event_payload": {
                "user_eid": student_1.eid,
                "accessible_products": [product_1_eid],
                "hierarchy_provider_uri": hierarchy_provider_1_uri,
            },
        },
    ]


@pytest.mark.asyncio
@freeze_time("2023-01-01")
async def test_redeem_license__200_ok_no_products__seat_expired(
    client: AsyncClient,
    create_license,
    update_license,
    teacher_1,
    student_1_class_1_memberships_authorization_token,
    student_1_class_1_memberships,
    student_1,
    hierarchy_provider_1_uri,
    product_1_eid,
):
    """
    License cannot be redeemed, because it has expired, but
    a seat already has been occupied.
    """
    license_uuid = "22222222-aea8-4de2-bcca-7b1945285502"
    await create_license(
        uuid=license_uuid,
        valid_from=datetime.date(2000, 1, 1),
        valid_to=datetime.date(2023, 1, 1),
    )
    await client.post(
        "/v1/member/permissions",
        json={"memberships": student_1_class_1_memberships},
        headers={
            "Authorization": f"Bearer {student_1_class_1_memberships_authorization_token}"
        },
    )
    # expire license ...
    await update_license(license_uuid, valid_to=datetime.date(2022, 1, 1))
    response = await client.post(
        "/v1/member/permissions",
        json={"memberships": student_1_class_1_memberships},
        headers={
            "Authorization": f"Bearer {student_1_class_1_memberships_authorization_token}"
        },
    )
    assert response.status_code == http_status.HTTP_200_OK
    assert [
        asdict(l_, dict_factory=dict_without_event_id)
        for l_ in (await query_event_log())[1:]
    ] == [
        {
            "event_type": str(EventType.SEAT_CREATED),
            "event_timestamp": datetime.datetime(
                2023, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc
            ),
            "event_version": 1,
            "event_payload": {
                "uuid": license_uuid,
                "status": str(SeatStatus.ACTIVE),
                "user_eid": student_1.eid,
                "is_occupied": True,
                "occupied_at": "2023-01-01T00:00:00+00:00",
                "last_accessed_at": "2023-01-01T00:00:00+00:00",
            },
        },
        {
            "event_type": str(EventType.PERMISSIONS_REQUESTED),
            "event_timestamp": datetime.datetime(
                2023, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc
            ),
            "event_version": 1,
            "event_payload": {
                "user_eid": student_1.eid,
                "accessible_products": [product_1_eid],
                "hierarchy_provider_uri": hierarchy_provider_1_uri,
            },
        },
        {
            "event_type": str(EventType.LICENSE_UPDATED),
            "event_timestamp": datetime.datetime(
                2023, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc
            ),
            "event_version": 1,
            "event_payload": {
                "uuid": license_uuid,
                "valid_to": "2022-01-01",
                "manager_eid": teacher_1.eid,
            },
        },
        {
            "event_type": str(EventType.SEAT_UPDATED),
            "event_timestamp": datetime.datetime(
                2023, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc
            ),
            "event_version": 1,
            "event_payload": {
                "uuid": license_uuid,
                "status": str(SeatStatus.EXPIRED),
                "user_eid": student_1.eid,
                "is_occupied": False,
                "occupied_at": "2023-01-01T00:00:00+00:00",
                "last_accessed_at": "2023-01-01T00:00:00+00:00",
            },
        },
        {
            "event_type": str(EventType.PERMISSIONS_REQUESTED),
            "event_timestamp": datetime.datetime(
                2023, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc
            ),
            "event_version": 1,
            "event_payload": {
                "user_eid": student_1.eid,
                "accessible_products": [],
                "hierarchy_provider_uri": hierarchy_provider_1_uri,
            },
        },
    ]
