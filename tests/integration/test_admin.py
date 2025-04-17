import datetime
import json

import pytest
from fastapi import status as http_status
from httpx import AsyncClient

from services.licensing.custom_types import SeatStatus


@pytest.mark.asyncio
async def test_get_license_multiple_seats__ok(
    client: AsyncClient,
    create_license,
    create_seat,
    admin_backoffice_authorization_token,
    student_1,
    student_2,
    student_3,
):
    #
    # checks 'licenses/<<license uuid>>' route even for already redeemed licenses
    # (This also checks the resolution of a bug, where we got a
    # 'Multiple rows were found when one or none was required' exception, when
    # requesting a license, that has already more than on seat redeemed.
    #
    license_uuid = "11111111-1111-1111-1111-111111111111"
    await create_license(
        id=1,
        uuid=license_uuid,
        manager_eid="someone@DE_bettermarks",
    )
    await create_seat(1, user_eid=student_1.eid)
    await create_seat(
        1, user_eid=student_2.eid, is_occupied=False, status=SeatStatus.EXPIRED
    )
    await create_seat(1, user_eid=student_3.eid)

    response = await client.get(
        f"/v1/admin/licenses/{license_uuid}",
        headers={"Authorization": f"Bearer {admin_backoffice_authorization_token}"},
    )
    assert response.status_code == http_status.HTTP_200_OK
    license_ = json.loads(response._content)
    assert license_["uuid"] == license_uuid
    assert license_["nof_occupied_seats"] == 2


@pytest.mark.asyncio
async def test_get_license_no_seat__ok(
    client: AsyncClient,
    create_license,
    create_seat,
    admin_backoffice_authorization_token,
    student_2,
):
    # checks 'licenses/<<license uuid>>' route with no seats attached
    license_uuid = "11111111-1111-1111-1111-111111111111"
    await create_license(
        id=1,
        uuid=license_uuid,
        manager_eid="someone@DE_bettermarks",
    )
    # only expired seat ...
    await create_seat(
        1, user_eid=student_2.eid, is_occupied=False, status=SeatStatus.EXPIRED
    )
    response = await client.get(
        f"/v1/admin/licenses/{license_uuid}",
        headers={"Authorization": f"Bearer {admin_backoffice_authorization_token}"},
    )
    assert response.status_code == http_status.HTTP_200_OK
    license_ = json.loads(response._content)
    assert license_["uuid"] == license_uuid
    assert license_["nof_occupied_seats"] == 0


async def test_admin__license_create__ok(
    client: AsyncClient,
    admin_license_example,
    admin_backoffice_authorization_token,
):
    response = await client.post(
        "/v1/admin/licenses",
        json=admin_license_example,
        headers={"Authorization": f"Bearer {admin_backoffice_authorization_token}"},
    )
    assert response.status_code == http_status.HTTP_201_CREATED


@pytest.mark.parametrize(("extra_seats", "result"), [(20, 20), (None, 0), (0, 0)])
async def test_admin__license_create__extra_seats(
    client: AsyncClient,
    admin_license_example,
    admin_backoffice_authorization_token,
    extra_seats,
    result,
):
    response = await client.post(
        "/v1/admin/licenses",
        json={**admin_license_example, "extra_seats": extra_seats},
        headers={"Authorization": f"Bearer {admin_backoffice_authorization_token}"},
    )
    assert response.status_code == http_status.HTTP_201_CREATED
    license_data = json.loads(response._content)
    assert license_data["extra_seats"] == result


@pytest.mark.parametrize(("nof_seats", "result"), [(20, 20), (None, -1), (0, 0)])
async def test_admin__license_create__nof_seats(
    client: AsyncClient,
    admin_license_example,
    admin_backoffice_authorization_token,
    nof_seats,
    result,
):
    response = await client.post(
        "/v1/admin/licenses",
        json={**admin_license_example, "nof_seats": nof_seats},
        headers={"Authorization": f"Bearer {admin_backoffice_authorization_token}"},
    )
    assert response.status_code == http_status.HTTP_201_CREATED
    license_data = json.loads(response._content)
    assert license_data["nof_seats"] == result


@pytest.mark.parametrize(
    "inbound_data",
    [
        {"manager_eid": "3@DE_bettermaks"},
        {"nof_seats": 30},
        {"nof_seats": 30, "manager_eid": "3@DE_bettermaks"},
    ],
)
async def test_admin__license_update__ok(
    client: AsyncClient,
    admin_license_example,
    admin_backoffice_authorization_token,
    inbound_data,
):
    """..."""
    # prepare target (initialization)
    response = await client.post(
        "/v1/admin/licenses",
        json=admin_license_example,
        headers={"Authorization": f"Bearer {admin_backoffice_authorization_token}"},
    )
    assert response.status_code == http_status.HTTP_201_CREATED
    license_data = json.loads(response._content)
    license_uuid = license_data["uuid"]

    # modify target
    response = await client.put(
        f"/v1/admin/licenses/{license_uuid}",
        json=inbound_data,
        headers={"Authorization": f"Bearer {admin_backoffice_authorization_token}"},
    )
    assert response.status_code == http_status.HTTP_200_OK

    # check response
    response = await client.get(
        f"/v1/admin/licenses/{license_uuid}",
        params=[],
        headers={"Authorization": f"Bearer {admin_backoffice_authorization_token}"},
    )
    assert response.status_code == http_status.HTTP_200_OK

    # check response data
    license_data = json.loads(response._content)
    for key, value in inbound_data.items():
        assert key in license_data
        assert value == license_data[key]


@pytest.mark.parametrize(
    ("original_data", "update_data", "res_nof_seats"),
    [
        pytest.param(
            {"nof_seats": 20}, {"nof_seats": 0}, 0, id="nof_seats from 20 to 0"
        ),
        pytest.param(
            {"nof_seats": 20},
            {"nof_seats": None},
            -1,
            id="nof_seats from 20 to implicit infinity",
        ),
        pytest.param(
            {"nof_seats": 20},
            {"nof_seats": -1},
            -1,
            id="nof_seats from 20 to explicit infinity",
        ),
        pytest.param(
            {"nof_seats": 20},
            {"notes": "hola"},
            20,
            id="nof_seats stays same",
        ),
        pytest.param(
            {"nof_seats": -1},
            {"nof_seats": None},
            -1,
            id="nof_seats from explicit infinity to implicit infinity",
        ),
        pytest.param(
            {"nof_seats": -1},
            {"nof_seats": 20},
            20,
            id="nof_seats from infinity to 20",
        ),
        pytest.param(
            {"nof_seats": -1},
            {"notes": "hola"},
            -1,
            id="nof_seats stays infinity",
        ),
    ],
)
async def test_admin__license_update__nof_seats(
    client: AsyncClient,
    admin_backoffice_authorization_token,
    admin_license_example,
    original_data,
    update_data,
    res_nof_seats,
):
    # prepare target (initialization)
    response = await client.post(
        "/v1/admin/licenses",
        json=admin_license_example | original_data,
        headers={"Authorization": f"Bearer {admin_backoffice_authorization_token}"},
    )
    assert response.status_code == http_status.HTTP_201_CREATED
    license_data = json.loads(response._content)
    license_uuid = license_data["uuid"]

    # modify target
    response = await client.put(
        f"/v1/admin/licenses/{license_uuid}",
        json=update_data,
        headers={"Authorization": f"Bearer {admin_backoffice_authorization_token}"},
    )
    assert response.status_code == http_status.HTTP_200_OK

    # check response
    response = await client.get(
        f"/v1/admin/licenses/{license_uuid}",
        params=[],
        headers={"Authorization": f"Bearer {admin_backoffice_authorization_token}"},
    )
    assert response.status_code == http_status.HTTP_200_OK

    # check response data
    license_data = json.loads(response._content)
    assert license_data["nof_seats"] == res_nof_seats


@pytest.mark.parametrize(
    ("original_data", "update_data", "res_extra_seats"),
    [
        pytest.param(
            {"extra_seats": 20}, {"extra_seats": 0}, 0, id="extra_seats from 20 to 0"
        ),
        pytest.param(
            {"extra_seats": 20},
            {"extra_seats": None},
            0,
            id="extra_seats from 20 to 0",
        ),
        pytest.param(
            {"extra_seats": 20},
            {"notes": "hola"},
            20,
            id="extra_seats stays same",
        ),
        pytest.param(
            {"extra_seats": 0},
            {"extra_seats": None},
            0,
            id="extra_seats from explicit 0 to implicit 0",
        ),
        pytest.param(
            {"extra_seats": None},
            {"extra_seats": 0},
            0,
            id="extra_seats from implicit 0 to explicit 0",
        ),
        pytest.param(
            {"extra_seats": 0},
            {"notes": "hola"},
            0,
            id="extra_seats stays 0",
        ),
        pytest.param(
            {"extra_seats": None},
            {"notes": "hola"},
            0,
            id="extra_seats stays implicit 0",
        ),
    ],
)
async def test_admin__license_update__extra_seats(
    client: AsyncClient,
    admin_backoffice_authorization_token,
    admin_license_example,
    original_data,
    update_data,
    res_extra_seats,
):
    # prepare target (initialization)
    response = await client.post(
        "/v1/admin/licenses",
        json=admin_license_example | original_data,
        headers={"Authorization": f"Bearer {admin_backoffice_authorization_token}"},
    )
    assert response.status_code == http_status.HTTP_201_CREATED
    license_data = json.loads(response._content)
    license_uuid = license_data["uuid"]

    # modify target
    response = await client.put(
        f"/v1/admin/licenses/{license_uuid}",
        json=update_data,
        headers={"Authorization": f"Bearer {admin_backoffice_authorization_token}"},
    )
    assert response.status_code == http_status.HTTP_200_OK

    # check response
    response = await client.get(
        f"/v1/admin/licenses/{license_uuid}",
        params=[],
        headers={"Authorization": f"Bearer {admin_backoffice_authorization_token}"},
    )
    assert response.status_code == http_status.HTTP_200_OK

    # check response data
    license_data = json.loads(response._content)
    assert license_data["extra_seats"] == res_extra_seats


@pytest.mark.asyncio
async def test_licenses__created_at_format(
    client: AsyncClient, admin_backoffice_authorization_token, admin_license_example
):
    response = await client.post(
        "/v1/admin/licenses",
        json=admin_license_example,
        headers={"Authorization": f"Bearer {admin_backoffice_authorization_token}"},
    )
    assert response.status_code == http_status.HTTP_201_CREATED

    response = await client.get(
        "/v1/admin/licenses",
        headers={"Authorization": f"Bearer {admin_backoffice_authorization_token}"},
    )
    assert response.status_code == http_status.HTTP_200_OK
    assert datetime.datetime.strptime(
        json.loads(response._content)["items"][0]["created_at"],
        "%Y-%m-%dT%H:%M:%S.%f+00:00",
    )
