import json
from typing import Tuple

from httpx import AsyncClient
from fastapi import status as http_status

import pytest


@pytest.mark.asyncio
async def test_admin_order_by_uuid_asc__ok(
    client: AsyncClient, licenses_route_admin: Tuple, create_many_licenses_with_seats
):
    await create_many_licenses_with_seats(10)
    _, route, token, _ = licenses_route_admin
    response = await client.get(
        f"{route}?order_by=uuid",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == http_status.HTTP_200_OK
    assert [i_["uuid"] for i_ in json.loads(response._content)["items"]][:2] == [
        "00000001-1111-1111-1111-111111111111",
        "00000002-1111-1111-1111-111111111111",
    ]


@pytest.mark.asyncio
async def test_admin_get_licenses_order_by_uuid_desc__ok(
    client: AsyncClient, licenses_route_admin: Tuple, create_many_licenses_with_seats
):
    await create_many_licenses_with_seats(10)
    _, route, token, _ = licenses_route_admin
    response = await client.get(
        f"{route}?order_by=-uuid",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == http_status.HTTP_200_OK
    assert [i_["uuid"] for i_ in json.loads(response._content)["items"]][:2] == [
        "00000010-1111-1111-1111-111111111111",
        "00000009-1111-1111-1111-111111111111",
    ]


@pytest.mark.asyncio
async def test_order_by_uuid_asc__ok(
    client: AsyncClient, licenses_route: Tuple, create_many_licenses_with_seats
):
    await create_many_licenses_with_seats(10)
    _, route, token, hierarchies = licenses_route
    response = await client.post(
        f"{route}?order_by=uuid",
        json={"hierarchies": hierarchies},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == http_status.HTTP_200_OK
    assert [i_["uuid"] for i_ in json.loads(response._content)["items"]][:2] == [
        "00000001-1111-1111-1111-111111111111",
        "00000002-1111-1111-1111-111111111111",
    ]


@pytest.mark.asyncio
async def test_get_licenses_order_by_uuid_desc__ok(
    client: AsyncClient, licenses_route: Tuple, create_many_licenses_with_seats
):
    await create_many_licenses_with_seats(10)
    _, route, token, hierarchies = licenses_route
    response = await client.post(
        f"{route}?order_by=-uuid",
        json={"hierarchies": hierarchies},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == http_status.HTTP_200_OK
    assert [i_["uuid"] for i_ in json.loads(response._content)["items"]][:2] == [
        "00000010-1111-1111-1111-111111111111",
        "00000009-1111-1111-1111-111111111111",
    ]
