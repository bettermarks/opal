import json
import pytest

from copy import deepcopy
from fastapi import status as http_status
from freezegun import freeze_time
from httpx import AsyncClient


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("additional_payload", "valid_from", "valid_to"),
    [
        pytest.param({}, "2023-01-01", "2023-02-26", id="default-duration"),
        pytest.param({"duration_weeks": 1}, "2023-01-01", "2023-01-08", id="1-week"),
    ],
)
@freeze_time("2023-01-01")
async def test_create_trial_license__ok(
    client: AsyncClient,
    teacher_1,
    teacher_1_hierarchies,
    teacher_1_memberships,
    teacher_1_memberships_authorization_token,
    teacher_1_hierarchies_authorization_token,
    teacher_1_trial_payload,
    additional_payload,
    valid_from,
    valid_to,
):
    """
    Yes, purchase a license!
    """
    payload = deepcopy(teacher_1_trial_payload) | additional_payload
    payload["memberships"] = teacher_1_memberships
    response = await client.post(
        "/v1/member/licenses/trial",
        json=payload,
        headers={
            "Authorization": f"Bearer {teacher_1_memberships_authorization_token}"
        },
    )
    assert response.status_code == http_status.HTTP_201_CREATED
    license_data = json.loads(response._content)
    license_uuid = license_data["uuid"]
    assert license_data == {
        "product_eid": teacher_1_trial_payload["product_eid"],
        "is_trial": True,
        "uuid": license_uuid,
        "valid_from": valid_from,
        "valid_to": valid_to,
        "owner_level": teacher_1_trial_payload["owner_level"],
        "owner_type": teacher_1_trial_payload["owner_type"],
        "nof_seats": 50,
        "nof_free_seats": 50,
        "nof_occupied_seats": 0,
        "extra_seats": 0,
    }
    # ok. we should have a license in the DB!
    response = await client.post(
        "/v1/hierarchy/licenses",
        json={"hierarchies": teacher_1_hierarchies},
        headers={
            "Authorization": f"Bearer {teacher_1_hierarchies_authorization_token}"
        },
    )
    licenses = json.loads(response._content)["items"]
    assert len(licenses) == 1
    assert "created_at" in licenses[0]
    licenses[0].pop("created_at")
    assert licenses[0] == {
        "is_trial": True,
        "nof_seats": teacher_1_trial_payload["nof_seats"],
        "nof_free_seats": teacher_1_trial_payload["nof_seats"],
        "nof_occupied_seats": 0,
        "extra_seats": 0,
        "owner_eids": [teacher_1_trial_payload["owner_eid"]],
        "owner_level": teacher_1_trial_payload["owner_level"],
        "owner_type": teacher_1_trial_payload["owner_type"],
        "product_eid": teacher_1_trial_payload["product_eid"],
        "uuid": license_uuid,
        "valid_from": valid_from,
        "valid_to": valid_to,
    }


@pytest.mark.asyncio
@freeze_time("2023-01-01")
async def test_create_trial_licenses__nok(
    client: AsyncClient,
    teacher_1_hierarchies,
    teacher_1_memberships,
    teacher_1_memberships_authorization_token,
    teacher_1_hierarchies_authorization_token,
    teacher_1_trial_payload,
):
    """
    Yes, purchase a license!
    """
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

    # try to create second trial license with same duration
    response_2 = await client.post(
        "/v1/member/licenses/trial",
        json=payload,
        headers={
            "Authorization": f"Bearer {teacher_1_memberships_authorization_token}"
        },
    )
    assert response_2.status_code == http_status.HTTP_409_CONFLICT

    # try to create second trial license with different duration
    response_3 = await client.post(
        "/v1/member/licenses/trial",
        json=payload | {"duration_weeks": 1},
        headers={
            "Authorization": f"Bearer {teacher_1_memberships_authorization_token}"
        },
    )
    assert response_3.status_code == http_status.HTTP_409_CONFLICT

    # ok. we should have only one license in the DB!
    response = await client.post(
        "/v1/hierarchy/licenses",
        json={"hierarchies": teacher_1_hierarchies},
        headers={
            "Authorization": f"Bearer {teacher_1_hierarchies_authorization_token}"
        },
    )
    licenses = json.loads(response._content)["items"]
    assert len(licenses) == 1


@pytest.mark.asyncio
@freeze_time("2023-01-10")
async def test_get_available_licenses__ok(
    client: AsyncClient,
    create_license,
    teacher_1_memberships_authorization_token,
    teacher_1_memberships,
    class_1,
    class_2,
):
    await create_license(
        uuid="11111111-aea8-4de2-bcca-7b1945285502",
        owner_type=class_1.type_,
        owner_level=class_1.level,
        owner_eids=[class_1.eid],
    )
    await create_license(
        uuid="22222222-aea8-4de2-bcca-7b1945285502",
        owner_type=class_2.type_,
        owner_level=class_2.level,
        owner_eids=[class_2.eid],
    )

    response = await client.post(
        "/v1/member/licenses?order_by=uuid",
        json={
            "memberships": teacher_1_memberships,
        },
        headers={
            "Authorization": f"Bearer {teacher_1_memberships_authorization_token}"
        },
    )
    assert response.status_code == http_status.HTTP_200_OK
    assert len(json.loads(response._content)["items"]) == 2
    assert json.loads(response._content)["items"] == [
        {
            "uuid": "11111111-aea8-4de2-bcca-7b1945285502",
            "valid_from": "2023-01-01",
            "valid_to": "2024-01-01",
            "owner_type": class_1.type_,
            "owner_level": class_1.level,
            "owner_eids": [class_1.eid],
            "is_trial": False,
            "nof_seats": 10,
            "nof_free_seats": 10,
            "nof_occupied_seats": 0,
            "extra_seats": 0,
            "product_eid": "product_1",
        },
        {
            "uuid": "22222222-aea8-4de2-bcca-7b1945285502",
            "valid_from": "2023-01-01",
            "valid_to": "2024-01-01",
            "owner_type": class_2.type_,
            "owner_level": class_2.level,
            "owner_eids": [class_2.eid],
            "is_trial": False,
            "nof_seats": 10,
            "nof_free_seats": 10,
            "nof_occupied_seats": 0,
            "extra_seats": 0,
            "product_eid": "product_1",
        },
    ]
