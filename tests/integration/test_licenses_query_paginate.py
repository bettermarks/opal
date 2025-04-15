import json
from typing import Tuple

from httpx import AsyncClient
from fastapi import status as http_status

import pytest

from services.licensing.main import ROUTE_PREFIX


@pytest.mark.asyncio
async def test_paginate__ok(
    client: AsyncClient, licenses_route: Tuple, create_many_licenses_with_seats
):
    await create_many_licenses_with_seats(10)
    _, route, token, hierarchies = licenses_route
    response = await client.post(
        f"{route}?order_by=uuid&page=1&size=3",
        json={"hierarchies": hierarchies},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == http_status.HTTP_200_OK
    assert [i_["uuid"] for i_ in json.loads(response._content)["items"]] == [
        "00000001-1111-1111-1111-111111111111",
        "00000002-1111-1111-1111-111111111111",
        "00000003-1111-1111-1111-111111111111",
    ]

    response = await client.post(
        f"{route}?order_by=uuid&page=1&size=4",
        json={"hierarchies": hierarchies},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == http_status.HTTP_200_OK
    assert [i_["uuid"] for i_ in json.loads(response._content)["items"]] == [
        "00000001-1111-1111-1111-111111111111",
        "00000002-1111-1111-1111-111111111111",
        "00000003-1111-1111-1111-111111111111",
        "00000004-1111-1111-1111-111111111111",
    ]

    response = await client.post(
        f"{route}?order_by=uuid&page=3&size=2",
        json={"hierarchies": hierarchies},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == http_status.HTTP_200_OK
    assert [i_["uuid"] for i_ in json.loads(response._content)["items"]] == [
        "00000005-1111-1111-1111-111111111111",
        "00000006-1111-1111-1111-111111111111",
    ]


@pytest.mark.asyncio
async def test_paginate_full__ok(
    client: AsyncClient, licenses_route: Tuple, create_many_licenses_with_seats
):
    await create_many_licenses_with_seats(10)
    _, route, token, hierarchies = licenses_route
    response = await client.post(
        f"{route}?order_by=uuid&page=3&size=3",
        json={"hierarchies": hierarchies},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == http_status.HTTP_200_OK
    result = json.loads(response._content)
    assert result["total"] == 10
    assert result["page"] == 3
    assert result["size"] == 3
    assert result["pages"] == 4
    assert result["links"] == {
        "first": f"{route}?order_by=uuid&size=3&page=1",
        "last": f"{route}?order_by=uuid&size=3&page=4",
        "self": f"{route}?order_by=uuid&page=3&size=3",
        "next": f"{route}?order_by=uuid&size=3&page=4",
        "prev": f"{route}?order_by=uuid&size=3&page=2",
    }


@pytest.mark.asyncio
async def test_admin_paginate__ok(
    client: AsyncClient, licenses_route_admin: Tuple, create_many_licenses_with_seats
):
    await create_many_licenses_with_seats(10)
    _, route, token, _ = licenses_route_admin
    response = await client.get(
        f"{route}?order_by=uuid&page=1&size=3",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == http_status.HTTP_200_OK
    assert [i_["uuid"] for i_ in json.loads(response._content)["items"]] == [
        "00000001-1111-1111-1111-111111111111",
        "00000002-1111-1111-1111-111111111111",
        "00000003-1111-1111-1111-111111111111",
    ]

    response = await client.get(
        f"{route}?order_by=uuid&page=1&size=4",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == http_status.HTTP_200_OK
    assert [i_["uuid"] for i_ in json.loads(response._content)["items"]] == [
        "00000001-1111-1111-1111-111111111111",
        "00000002-1111-1111-1111-111111111111",
        "00000003-1111-1111-1111-111111111111",
        "00000004-1111-1111-1111-111111111111",
    ]

    response = await client.get(
        f"{route}?order_by=uuid&page=3&size=2",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == http_status.HTTP_200_OK
    assert [i_["uuid"] for i_ in json.loads(response._content)["items"]] == [
        "00000005-1111-1111-1111-111111111111",
        "00000006-1111-1111-1111-111111111111",
    ]


@pytest.mark.asyncio
async def test_admin_paginate_full__ok(
    client: AsyncClient, licenses_route_admin: Tuple, create_many_licenses_with_seats
):
    await create_many_licenses_with_seats(10)
    _, route, token, _ = licenses_route_admin
    response = await client.get(
        f"{route}?order_by=uuid&page=3&size=3",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == http_status.HTTP_200_OK
    result = json.loads(response._content)
    assert result["total"] == 10
    assert result["page"] == 3
    assert result["size"] == 3
    assert result["pages"] == 4
    assert result["links"] == {
        "first": f"{route}?order_by=uuid&size=3&page=1",
        "last": f"{route}?order_by=uuid&size=3&page=4",
        "self": f"{route}?order_by=uuid&page=3&size=3",
        "next": f"{route}?order_by=uuid&size=3&page=4",
        "prev": f"{route}?order_by=uuid&size=3&page=2",
    }
