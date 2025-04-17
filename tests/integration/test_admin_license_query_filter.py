import datetime
import json

from httpx import AsyncClient
from fastapi import status as http_status
from freezegun import freeze_time

import pytest

from services.licensing.custom_types import SeatStatus


@pytest.fixture
async def licenses_for_filtering(
    create_license,
    product_1_eid,
    product_2_eid,
    teacher_1,
    teacher_2,
    class_1,
    class_2,
    school_1,
    school_2,
):
    i_ = 0
    for manager_eid in [teacher_1.eid, teacher_2.eid]:
        for owner in [class_1, class_2, school_1, school_2]:
            for product_eid in [product_1_eid, product_2_eid]:
                i_ += 1
                await create_license(
                    id=i_,
                    uuid=f"{i_:08d}-1111-1111-1111-111111111111",
                    product_eid=product_eid,
                    manager_eid=manager_eid,
                    owner_type=owner.type_,
                    owner_level=owner.level,
                    owner_eids=[owner.eid],
                    valid_from=datetime.date(2023, 1, 1),
                    valid_to=datetime.date(2024, 1, 1),
                )


@pytest.fixture(
    params=[
        "manager_eid=teacher_1.eid",
        "manager_eid=teacher_2.eid",
        "manager_eid=DE_bettermarks",
        "manager_eid=DE_bet",
        "manager_eid=CH_bettermarks",
        "manager_eid=CH_bet",
        "manager_eid=unknown",
        "product_eid=product_1_eid",
        "product_eid=product_2_eid",
        "product_eid=pro*",
        "product_eid=unknown",
        "owner_eid=class_1.eid",
        "owner_eid=class_2.eid",
        "owner_eid=class*",
        "owner_eid=school_1.eid",
        "owner_eid=school_2.eid",
        "owner_eid=unknown",
        "owner_level=1",
        "owner_level=2",
        "owner_level=-1",
        "owner_type=class",
        "owner_type=school",
        "owner_type=unknown",
        "is_trial=True",
        "is_trial=False",
        "valid_from=2022-12-31",
        "valid_from=2023-12-31",
        "valid_to=2022-12-31",
        "valid_to=2024-12-31",
        "valid_from=2022-05-31&valid_to=2025-10-31",
    ]
)
def licenses_filters(
    request,
    product_1_eid,
    product_2_eid,
    teacher_1,
    teacher_2,
    class_1,
    class_2,
    school_1,
    school_2,
):
    match request.param:
        case "manager_eid=teacher_1.eid":
            return [("manager_eid", teacher_1.eid)], [8, 8]
        case "manager_eid=teacher_2.eid":
            return [("manager_eid", teacher_2.eid)], [8, 0]
        case "manager_eid=DE_bettermarks":
            return [("manager_eid", "DE_bettermarks")], [8, 8]
        case "manager_eid=DE_bet":
            return [("manager_eid", "DE_bet")], [8, 8]
        case "manager_eid=CH_bettermarks":
            return [("manager_eid", "CH_bettermarks")], [8, 0]
        case "manager_eid=CH_bet":
            return [("manager_eid", "CH_bet")], [8, 0]
        case "manager_eid=unknown":
            return [("manager_eid", "unknown")], [0, 0]
        case "product_eid=product_1_eid":
            return [("product_eid", product_1_eid)], [8, 4]
        case "product_eid=product_2_eid":
            return [("product_eid", product_2_eid)], [8, 4]
        case "product_eid=pro*":
            return [("product_eid", "pro")], [16, 8]
        case "product_eid=unknown":
            return [("product_eid", "unknown")], [0, 0]
        case "owner_eid=class_1.eid":
            return [("owner_eid", class_1.eid)], [4, 2]
        case "owner_eid=class_2.eid":
            return [("owner_eid", class_2.eid)], [4, 2]
        case "owner_eid=class*":
            return [("owner_eid", "class")], [8, 4]
        case "owner_eid=school_1.eid":
            return [("owner_eid", school_1.eid)], [4, 2]
        case "owner_eid=school_2.eid":
            return [("owner_eid", school_2.eid)], [4, 2]
        case "owner_eid=unknown":
            return [("owner_eid", "unknown")], [0, 0]
        case "owner_level=1":
            return [("owner_level", 1)], [8, 4]
        case "owner_level=2":
            return [("owner_level", 2)], [8, 4]
        case "owner_level=-1":
            return [("owner_level", -1)], [0, 0]
        case "owner_type=class":
            return [("owner_type", "class")], [8, 4]
        case "owner_type=school":
            return [("owner_type", "school")], [8, 4]
        case "owner_type=unknown":
            return [("owner_type", "unknown")], [0, 0]
        case "is_trial=True":
            return [("is_trial", True)], [0, 0]
        case "is_trial=False":
            return [("is_trial", False)], [16, 8]
        case "valid_from=2022-12-31":
            return [("valid_from", datetime.date(2022, 12, 31))], [16, 8]
        case "valid_from=2023-12-31":
            return [("valid_from", datetime.date(2023, 12, 31))], [0, 0]
        case "valid_to=2022-12-31":
            return [("valid_to", datetime.date(2022, 12, 31))], [0, 0]
        case "valid_to=2024-12-31":
            return [("valid_to", datetime.date(2024, 12, 31))], [16, 8]
        case "valid_from=2022-05-31&valid_to=2025-10-31":
            return [
                ("valid_from", datetime.date(2022, 5, 31)),
                ("valid_to", datetime.date(2025, 10, 31)),
            ], [16, 8]
        case _:
            raise ValueError


@pytest.mark.parametrize(
    "token_type", ["without_restriction_filters", "with_restriction_filters"]
)
@pytest.mark.asyncio
async def test_licenses_filter__ok(
    token_type: str,
    client: AsyncClient,
    licenses_filters,
    licenses_for_filtering,  # needed, do not remove
    admin_backoffice_authorization_token,
    admin_backoffice_authorization_token_with_filter_restrictions,
):
    if token_type == "without_restriction_filters":
        token = admin_backoffice_authorization_token
        expected_index = 0
    else:
        token = admin_backoffice_authorization_token_with_filter_restrictions
        expected_index = 1

    filter_params, expected = licenses_filters
    filter_string = "&".join([f"{k}={v}" for k, v in filter_params])
    response = await client.get(
        f"/v1/admin/licenses?{filter_string}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == http_status.HTTP_200_OK
    assert len(json.loads(response._content)["items"]) == expected[expected_index]


@freeze_time("2023-01-01")
@pytest.mark.parametrize(
    "token_type", ["without_restriction_filters", "with_restriction_filters"]
)
@pytest.mark.asyncio
async def test_license_filter__ok(
    token_type: str,
    client: AsyncClient,
    create_license,
    create_seat,
    admin_backoffice_authorization_token,
    admin_backoffice_authorization_token_with_filter_restrictions,
):
    await create_license(
        id=1,
        uuid="11111111-1111-1111-1111-111111111111",
        manager_eid="someone@DE_bettermarks",
    )
    await create_seat(1)
    await create_license(
        id=2,
        uuid="22222222-1111-1111-1111-111111111111",
        manager_eid="someone@CH_bettermarks",
    )

    if token_type == "without_restriction_filters":
        token = admin_backoffice_authorization_token
        id_to_fetch, expected_is_none = "11111111-1111-1111-1111-111111111111", False
    else:
        token = admin_backoffice_authorization_token_with_filter_restrictions
        id_to_fetch, expected_is_none = "22222222-1111-1111-1111-111111111111", True

    response = await client.get(
        f"/v1/admin/licenses/{id_to_fetch}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == http_status.HTTP_200_OK
    assert (json.loads(response._content) is None) == expected_is_none


@freeze_time("2023-01-01")
@pytest.mark.parametrize(
    "redeemed_seats_percentage", [10, 20, 40, 50, 80, 90, 100, 110]
)
@pytest.mark.asyncio
async def test_license_filter_redeemed_seats__ok(
    redeemed_seats_percentage: int,
    client: AsyncClient,
    create_license,
    create_seat,
    class_1,
    class_2,
    admin_backoffice_authorization_token,
):
    # tests for special aggregation filters: redeemed_seats
    # test should return a matching license, if percentage of redeemed seats
    # (occupied seats) is at least the given number. We apply tests for
    # percentages [10, 20, 40, 50, 80, 90, 100, 110]
    nof_total_seats = 10
    nof_redeemed_seats = int(redeemed_seats_percentage / 100.0 * nof_total_seats)
    await create_license(
        id=1,
        uuid="11111111-1111-1111-1111-111111111111",
        owner_eids=[class_1.eid, class_2.eid],
        nof_seats=nof_total_seats,
    )
    for i_ in range(1, nof_redeemed_seats):
        await create_seat(1, user_eid=f"user_{i_}")  # regular seats
    await create_seat(  # 1 expired seat
        1,
        user_eid=f"user_{nof_redeemed_seats}",
        is_occupied=False,
        status=SeatStatus.EXPIRED,
    )
    # should not match, one seat is missing to reach percentage
    response = await client.get(
        f"/v1/admin/licenses?redeemed_seats={redeemed_seats_percentage}",
        headers={"Authorization": f"Bearer {admin_backoffice_authorization_token}"},
    )
    assert response.status_code == http_status.HTTP_200_OK
    assert len(json.loads(response._content)["items"]) == 0

    # ok, now it should match, as we have enough seats!
    await create_seat(1, user_eid=f"user_{nof_redeemed_seats}")
    response = await client.get(
        f"/v1/admin/licenses?redeemed_seats={redeemed_seats_percentage}",
        headers={"Authorization": f"Bearer {admin_backoffice_authorization_token}"},
    )
    assert response.status_code == http_status.HTTP_200_OK
    assert len(json.loads(response._content)["items"]) == 1
