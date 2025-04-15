#
# purchase license tests
#


import pytest
from fastapi import status as http_status
from httpx import AsyncClient


import json


@pytest.mark.asyncio
async def test_purchase_license__ok(
    client: AsyncClient,
    teacher_1,
    teacher_1_hierarchies,
    teacher_1_shop_authorization_token,
    teacher_1_hierarchies_authorization_token,
    teacher_1_purchase_payload,
):
    """
    Yes, purchase a license!
    """
    response = await client.post(
        "/v1/order/licenses",
        json={},
        headers={"Authorization": f"Bearer {teacher_1_shop_authorization_token}"},
    )
    assert response.status_code == http_status.HTTP_201_CREATED

    license_data = json.loads(response._content)
    license_uuid = license_data["uuid"]
    assert license_data == {
        "product_eid": teacher_1_purchase_payload["product_eid"],
        "is_trial": False,
        "uuid": license_uuid,
        "owner_level": teacher_1_purchase_payload["owner_level"],
        "owner_type": teacher_1_purchase_payload["owner_type"],
        "valid_from": teacher_1_purchase_payload["valid_from"],
        "valid_to": teacher_1_purchase_payload["valid_to"],
        "nof_seats": teacher_1_purchase_payload["nof_seats"],
        "nof_free_seats": teacher_1_purchase_payload["nof_seats"],
        "nof_occupied_seats": 0,
        "extra_seats": teacher_1_purchase_payload["extra_seats"],
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
    # drop fuzzy parameter `created_at` from assert
    assert "created_at" in licenses[0]
    licenses[0].pop("created_at")
    # then check payload
    assert licenses[0] == {
        "is_trial": False,
        "nof_seats": teacher_1_purchase_payload["nof_seats"],
        "nof_free_seats": teacher_1_purchase_payload["nof_seats"],
        "nof_occupied_seats": 0,
        "extra_seats": teacher_1_purchase_payload["extra_seats"],
        "owner_eids": teacher_1_purchase_payload["owner_eids"],
        "owner_level": teacher_1_purchase_payload["owner_level"],
        "owner_type": teacher_1_purchase_payload["owner_type"],
        "product_eid": teacher_1_purchase_payload["product_eid"],
        "uuid": license_uuid,
        "valid_from": teacher_1_purchase_payload["valid_from"],
        "valid_to": teacher_1_purchase_payload["valid_to"],
    }


@pytest.mark.asyncio
async def test_purchase_license__409_license_purchased_twice(
    client: AsyncClient,
    teacher_1_shop_authorization_token,
    teacher_1_purchase_payload,
):
    """
    Try to purchase the same license twice
    """
    response = await client.post(
        "/v1/order/licenses",
        json={},
        headers={"Authorization": f"Bearer {teacher_1_shop_authorization_token}"},
    )
    assert response.status_code == http_status.HTTP_201_CREATED
    response = await client.post(
        "/v1/order/licenses",
        json={},
        headers={"Authorization": f"Bearer {teacher_1_shop_authorization_token}"},
    )
    assert response.status_code == http_status.HTTP_409_CONFLICT
    assert json.loads(response._content) == {
        "detail": (
            "License purchase failed: A license for at least one of the "
            "entered owner EIDs already exists"
        )
    }


@pytest.mark.asyncio
async def test_upgrade_license__ok(
    create_license,
    client: AsyncClient,
    teacher_1_shop_authorization_token,
):
    """
    Successfully upgrade a license (increase the number of seats).
    """

    # init a license with 10 seats
    await create_license(id=1, uuid="11111111-2222-1111-1111-111111111111")

    # upgrade the license to 100 seats
    response = await client.put(
        "/v1/order/licenses/11111111-2222-1111-1111-111111111111",
        data={},
        headers={"Authorization": f"Bearer {teacher_1_shop_authorization_token}"},
    )
    assert response.status_code == http_status.HTTP_200_OK

    updated_license_data = json.loads(response.read())
    assert updated_license_data["uuid"] == "11111111-2222-1111-1111-111111111111"
    assert updated_license_data["nof_seats"] == 100
