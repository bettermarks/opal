import datetime
import json

from httpx import AsyncClient
from fastapi import status as http_status
from freezegun import freeze_time

import pytest

from services.licensing import settings
from services.licensing.custom_types import SeatStatus
from services.licensing.tokens import get_expiration_timestamp
from tests.integration.conftest import check_license_service_token


#
# redeeming tests
#


@pytest.mark.asyncio
@freeze_time("2023-01-01")
async def test_redeem_license__200_ok_one_product(
    client: AsyncClient,
    create_license,
    student_1_class_1_memberships_authorization_token,
    student_1_class_1_memberships,
    teacher_1_hierarchies_authorization_token,
    product_1_eid,
    student_1,
    teacher_1_hierarchies,
):
    """License redeeming ok, seat gets occupied"""
    await create_license(uuid="22222222-aea8-4de2-bcca-7b1945285502")

    response = await client.post(
        "/v1/member/permissions",
        json={"memberships": student_1_class_1_memberships},
        headers={
            "Authorization": f"Bearer {student_1_class_1_memberships_authorization_token}"
        },
    )
    assert response.status_code == http_status.HTTP_200_OK
    assert check_license_service_token(json.loads(response._content)) == {
        "hierarchy_provider_uri": "http://example_hierarchy_provider.com",
        "exp": get_expiration_timestamp(settings.permissions_token_livetime_secs),
        "iss": settings.licensing_service_url,
        "sub": student_1.eid,
        "accessible_products": [product_1_eid],
    }

    # check seats in db
    response = await client.post(
        "/v1/hierarchy/licenses",
        json={"hierarchies": teacher_1_hierarchies},
        headers={
            "Authorization": f"Bearer {teacher_1_hierarchies_authorization_token}"
        },
    )
    licenses = json.loads(response._content)["items"]
    assert len(licenses) == 1
    assert licenses[0]["nof_occupied_seats"] == 1
    assert (
        licenses[0]["nof_seats"] - licenses[0]["nof_occupied_seats"]
        == licenses[0]["nof_free_seats"]
    )


@pytest.mark.asyncio
async def test_redeem_license__200_ok_one_product_two_times(
    client: AsyncClient,
    create_license,
    student_1_class_1_memberships_authorization_token,
    student_1_class_1_memberships,
    teacher_1_hierarchies_authorization_token,
    product_1_eid,
    teacher_1_hierarchies,
):
    """License redeeming ok, seat is already occupied"""
    this_year: int = datetime.datetime.now().year
    await create_license(
        uuid="22222222-aea8-4de2-bcca-7b1945285502",
        valid_from=datetime.date(this_year, 1, 1),
        valid_to=datetime.date(this_year + 1, 1, 1),
    )

    # todo: another duplication case?
    await client.post(
        "/v1/member/permissions",
        json={"memberships": student_1_class_1_memberships},
        headers={
            "Authorization": f"Bearer {student_1_class_1_memberships_authorization_token}"
        },
    )
    response = await client.post(
        "/v1/member/permissions",
        json={"memberships": student_1_class_1_memberships},
        headers={
            "Authorization": f"Bearer {student_1_class_1_memberships_authorization_token}"
        },
    )
    assert response.status_code == http_status.HTTP_200_OK
    assert check_license_service_token(json.loads(response._content))[
        "accessible_products"
    ] == [product_1_eid]

    # check seats in db
    response = await client.post(
        "/v1/hierarchy/licenses",
        json={"hierarchies": teacher_1_hierarchies},
        headers={
            "Authorization": f"Bearer {teacher_1_hierarchies_authorization_token}"
        },
    )
    licenses = json.loads(response._content)["items"]
    assert len(licenses) == 1
    assert licenses[0]["nof_occupied_seats"] == 1
    assert (
        licenses[0]["nof_seats"] - licenses[0]["nof_occupied_seats"]
        == licenses[0]["nof_free_seats"]
    )


@pytest.mark.asyncio
async def test_redeem_license__200_ok_two_products(
    client: AsyncClient,
    create_license,
    student_1_class_1_memberships_authorization_token,
    student_1_class_1_memberships,
    teacher_1_hierarchies_authorization_token,
    product_1_eid,
    product_2_eid,
    teacher_1_hierarchies,
):
    """License redeeming ok, seat is occupied"""
    this_year: int = datetime.datetime.now().year
    await create_license(
        uuid="11111111-aea8-4de2-bcca-7b1945285502",
        valid_from=datetime.date(this_year, 1, 1),
        valid_to=datetime.date(this_year + 1, 1, 1),
    )
    await create_license(
        uuid="22222222-aea8-4de2-bcca-7b1945285502",
        product_eid=product_2_eid,
        valid_from=datetime.date(this_year, 1, 1),
        valid_to=datetime.date(this_year + 1, 1, 1),
    )

    response = await client.post(
        "/v1/member/permissions",
        json={"memberships": student_1_class_1_memberships},
        headers={
            "Authorization": f"Bearer {student_1_class_1_memberships_authorization_token}"
        },
    )

    assert response.status_code == http_status.HTTP_200_OK
    assert set(
        check_license_service_token(json.loads(response._content))[
            "accessible_products"
        ]
    ) == {
        product_1_eid,
        product_2_eid,
    }

    # check seats in db
    response = await client.post(
        "/v1/hierarchy/licenses",
        json={"hierarchies": teacher_1_hierarchies},
        headers={
            "Authorization": f"Bearer {teacher_1_hierarchies_authorization_token}"
        },
    )
    licenses = json.loads(response._content)["items"]
    assert len(licenses) == 2
    assert licenses[0]["nof_occupied_seats"] == 1
    assert (
        licenses[0]["nof_seats"] - licenses[0]["nof_occupied_seats"]
        == licenses[0]["nof_free_seats"]
    )
    assert licenses[1]["nof_occupied_seats"] == 1
    assert (
        licenses[1]["nof_seats"] - licenses[1]["nof_occupied_seats"]
        == licenses[1]["nof_free_seats"]
    )


@pytest.mark.asyncio
@freeze_time("2023-01-01")
async def test_redeem_license__200_ok_no_products__expired_license(
    client: AsyncClient,
    create_license,
    student_1_class_1_memberships_authorization_token,
    student_1_class_1_memberships,
    teacher_1_hierarchies_authorization_token,
    teacher_1_hierarchies,
):
    """
    License cannot be redeemed, because it has expired.
    """
    await create_license(
        uuid="22222222-aea8-4de2-bcca-7b1945285502",
        valid_from=datetime.date(2000, 1, 1),
        valid_to=datetime.date(2022, 12, 31),
    )

    response = await client.post(
        "/v1/member/permissions",
        json={"memberships": student_1_class_1_memberships},
        headers={
            "Authorization": f"Bearer {student_1_class_1_memberships_authorization_token}"
        },
    )
    assert response.status_code == http_status.HTTP_200_OK
    assert (
        check_license_service_token(json.loads(response._content))[
            "accessible_products"
        ]
        == []
    )

    # check seats in db
    response = await client.post(
        "/v1/hierarchy/licenses",
        json={"hierarchies": teacher_1_hierarchies},
        headers={
            "Authorization": f"Bearer {teacher_1_hierarchies_authorization_token}"
        },
    )
    licenses = json.loads(response._content)["items"]
    assert len(licenses) == 1
    assert licenses[0]["nof_occupied_seats"] == 0
    assert licenses[0]["nof_seats"] == licenses[0]["nof_free_seats"]


@pytest.mark.asyncio
@freeze_time("2023-01-01")
async def test_redeem_license__200_ok_no_products__seat_expired(
    client: AsyncClient,
    create_license,
    update_license,
    student_1_class_1_memberships_authorization_token,
    student_1_class_1_memberships,
    teacher_1_hierarchies_authorization_token,
    product_1_eid,
    teacher_1_hierarchies,
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

    response = await client.post(
        "/v1/member/permissions",
        json={"memberships": student_1_class_1_memberships},
        headers={
            "Authorization": f"Bearer {student_1_class_1_memberships_authorization_token}"
        },
    )
    assert response.status_code == http_status.HTTP_200_OK
    assert check_license_service_token(json.loads(response._content))[
        "accessible_products"
    ] == [product_1_eid]

    # check seats in db
    response = await client.post(
        "/v1/hierarchy/licenses",
        json={"hierarchies": teacher_1_hierarchies},
        headers={
            "Authorization": f"Bearer {teacher_1_hierarchies_authorization_token}"
        },
    )
    licenses = json.loads(response._content)["items"]
    assert len(licenses) == 1
    assert licenses[0]["nof_occupied_seats"] == 1
    assert (
        licenses[0]["nof_seats"] - licenses[0]["nof_occupied_seats"]
        == licenses[0]["nof_free_seats"]
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
    assert (
        check_license_service_token(json.loads(response._content))[
            "accessible_products"
        ]
        == []
    )
    # check seats in db
    response = await client.post(
        "/v1/hierarchy/licenses",
        json={"hierarchies": teacher_1_hierarchies},
        headers={
            "Authorization": f"Bearer {teacher_1_hierarchies_authorization_token}"
        },
    )
    licenses = json.loads(response._content)["items"]
    assert len(licenses) == 1
    assert licenses[0]["nof_occupied_seats"] == 0
    assert licenses[0]["nof_seats"] == licenses[0]["nof_free_seats"]


@pytest.mark.asyncio
async def test_redeem_license__200_ok_no_products__seat_no_member(
    client: AsyncClient,
    create_license,
    product_1_eid,
    student_1_class_1_memberships_authorization_token,
    student_1_class_1_memberships,
    student_1_class_2_memberships_authorization_token,
    student_1_class_2_memberships,
    teacher_1_hierarchies_authorization_token,
    teacher_1_hierarchies,
):
    """
    License cannot be redeemed, because student is no longer member, but
    a seat already has been occupied.
    """
    this_year: int = datetime.datetime.now().year
    await create_license(
        uuid="22222222-aea8-4de2-bcca-7b1945285502",
        valid_from=datetime.date(this_year, 1, 1),
        valid_to=datetime.date(this_year + 1, 1, 1),
    )
    response = await client.post(
        "/v1/member/permissions",
        json={"memberships": student_1_class_1_memberships},
        headers={
            "Authorization": f"Bearer {student_1_class_1_memberships_authorization_token}"
        },
    )
    assert response.status_code == http_status.HTTP_200_OK
    assert check_license_service_token(json.loads(response._content))[
        "accessible_products"
    ] == [product_1_eid]

    response = await client.post(
        "/v1/hierarchy/licenses",
        json={"hierarchies": teacher_1_hierarchies},
        headers={
            "Authorization": f"Bearer {teacher_1_hierarchies_authorization_token}"
        },
    )
    licenses = json.loads(response._content)["items"]
    assert len(licenses) == 1
    assert licenses[0]["nof_occupied_seats"] == 1
    assert (
        licenses[0]["nof_seats"] - licenses[0]["nof_occupied_seats"]
        == licenses[0]["nof_free_seats"]
    )

    # student1 is no longer in class 1, but class2!
    response = await client.post(
        "/v1/member/permissions",
        json={"memberships": student_1_class_2_memberships},
        headers={
            "Authorization": f"Bearer {student_1_class_2_memberships_authorization_token}"
        },
    )
    assert response.status_code == http_status.HTTP_200_OK
    assert (
        check_license_service_token(json.loads(response._content))[
            "accessible_products"
        ]
        == []
    )
    # check seats in db
    response = await client.post(
        "/v1/hierarchy/licenses",
        json={"hierarchies": teacher_1_hierarchies},
        headers={
            "Authorization": f"Bearer {teacher_1_hierarchies_authorization_token}"
        },
    )
    licenses = json.loads(response._content)["items"]
    assert len(licenses) == 1
    assert licenses[0]["nof_occupied_seats"] == 0
    assert licenses[0]["nof_seats"] == licenses[0]["nof_free_seats"]


@pytest.mark.asyncio
@freeze_time("2023-01-01")
async def test_redeem_license__200_ok_no_overredeeming(
    client: AsyncClient,
    create_license,
    student_2,
    student_1_class_1_memberships_authorization_token,
    student_1_class_1_memberships,
    student_2_class_1_memberships_authorization_token,
    student_2_class_1_memberships,
    teacher_1_hierarchies_authorization_token,
    teacher_1_hierarchies,
):
    """
    License redeeming ok, seat gets occupied, but 'overredeeming is prohibited
    """
    await create_license(uuid="22222222-aea8-4de2-bcca-7b1945285502", nof_seats=1)

    response = await client.post(
        "/v1/member/permissions",
        json={"memberships": student_1_class_1_memberships},
        headers={
            "Authorization": f"Bearer {student_1_class_1_memberships_authorization_token}"
        },
    )
    assert response.status_code == http_status.HTTP_200_OK

    # student2 should not be able to redeem
    response = await client.post(
        "/v1/member/permissions",
        json={"memberships": student_2_class_1_memberships},
        headers={
            "Authorization": f"Bearer {student_2_class_1_memberships_authorization_token}"
        },
    )
    assert response.status_code == http_status.HTTP_200_OK
    assert check_license_service_token(json.loads(response._content)) == {
        "hierarchy_provider_uri": "http://example_hierarchy_provider.com",
        "exp": get_expiration_timestamp(settings.permissions_token_livetime_secs),
        "iss": settings.licensing_service_url,
        "sub": student_2.eid,
        "accessible_products": [],
    }

    # check seats in db
    response = await client.post(
        "/v1/hierarchy/licenses",
        json={"hierarchies": teacher_1_hierarchies},
        headers={
            "Authorization": f"Bearer {teacher_1_hierarchies_authorization_token}"
        },
    )
    licenses = json.loads(response._content)["items"]
    assert len(licenses) == 1
    assert licenses[0]["nof_occupied_seats"] == 1
    assert (
        licenses[0]["nof_seats"] - licenses[0]["nof_occupied_seats"]
        == licenses[0]["nof_free_seats"]
    )


@pytest.mark.asyncio
@freeze_time("2023-01-01")
async def test_redeem_license__200_ok_no_overredeeming_extra_seats(
    client: AsyncClient,
    create_license,
    product_1_eid,
    student_2,
    student_3,
    student_1_class_1_memberships_authorization_token,
    student_1_class_1_memberships,
    student_2_class_1_memberships_authorization_token,
    student_2_class_1_memberships,
    student_3_class_1_memberships_authorization_token,
    student_3_class_1_memberships,
    teacher_1_hierarchies_authorization_token,
    teacher_1_hierarchies,
):
    """
    License redeeming ok, seat gets occupied, extra seats is being used,
    but 'overredeeming is prohibited
    """
    await create_license(
        uuid="22222222-aea8-4de2-bcca-7b1945285502", nof_seats=1, extra_seats=1
    )

    # ok student 1 has redeemed successfully ...
    await client.post(
        "/v1/member/permissions",
        json={"memberships": student_1_class_1_memberships},
        headers={
            "Authorization": f"Bearer {student_1_class_1_memberships_authorization_token}"
        },
    )

    # student2 should be able to redeem (and use extra seats!)
    response = await client.post(
        "/v1/member/permissions",
        json={"memberships": student_2_class_1_memberships},
        headers={
            "Authorization": f"Bearer {student_2_class_1_memberships_authorization_token}"
        },
    )
    assert response.status_code == http_status.HTTP_200_OK
    assert check_license_service_token(json.loads(response._content)) == {
        "hierarchy_provider_uri": "http://example_hierarchy_provider.com",
        "exp": get_expiration_timestamp(settings.permissions_token_livetime_secs),
        "iss": settings.licensing_service_url,
        "sub": student_2.eid,
        "accessible_products": [product_1_eid],
    }

    # student3 should NOT be able to redeem
    response = await client.post(
        "/v1/member/permissions",
        json={"memberships": student_3_class_1_memberships},
        headers={
            "Authorization": f"Bearer {student_3_class_1_memberships_authorization_token}"
        },
    )
    assert response.status_code == http_status.HTTP_200_OK
    assert check_license_service_token(json.loads(response._content)) == {
        "hierarchy_provider_uri": "http://example_hierarchy_provider.com",
        "exp": get_expiration_timestamp(settings.permissions_token_livetime_secs),
        "iss": settings.licensing_service_url,
        "sub": student_3.eid,
        "accessible_products": [],
    }

    # check seats in db
    response = await client.post(
        "/v1/hierarchy/licenses",
        json={"hierarchies": teacher_1_hierarchies},
        headers={
            "Authorization": f"Bearer {teacher_1_hierarchies_authorization_token}"
        },
    )
    licenses = json.loads(response._content)["items"]
    assert len(licenses) == 1
    assert licenses[0]["nof_occupied_seats"] == 2
    assert licenses[0]["nof_seats"] == 1
    assert licenses[0]["nof_free_seats"] == 0
