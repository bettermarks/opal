import datetime
from freezegun import freeze_time
import pytest
from fastapi import status as http_status
from httpx import AsyncClient


import json


@pytest.mark.asyncio
async def test_get_managed_licenses__ok(
    client: AsyncClient,
    create_license,
    teacher_1_hierarchies_authorization_token,
    teacher_1,
    teacher_1_hierarchies,
    teacher_2,
    product_1_eid,
    class_1,
    school_1,
):
    await create_license(uuid="11111111-aea8-4de2-bcca-7b1945285502")
    await create_license(
        uuid="11111111-2f05-4211-8eb4-a03b01a047a5",
        owner_type=school_1.type_,
        owner_level=school_1.level,
        owner_eids=[school_1.eid],
    )
    await create_license(
        uuid="22222222-aea8-4de2-bcca-7b1945285502", manager_eid=teacher_2.eid
    )

    response = await client.post(
        "/v1/hierarchy/licenses",
        json={"hierarchies": teacher_1_hierarchies},
        headers={
            "Authorization": f"Bearer {teacher_1_hierarchies_authorization_token}"
        },
    )
    assert response.status_code == http_status.HTTP_200_OK
    assert json.loads(response._content)["items"] == [
        {
            "uuid": "11111111-aea8-4de2-bcca-7b1945285502",
            "valid_from": "2023-01-01",
            "valid_to": "2024-01-01",
            "created_at": "2023-01-01T00:00:00+00:00",
            "owner_type": class_1.type_,
            "owner_level": class_1.level,
            "owner_eids": [class_1.eid],
            "is_trial": False,
            "nof_seats": 10,
            "nof_free_seats": 10,
            "nof_occupied_seats": 0,
            "extra_seats": 0,
            "product_eid": product_1_eid,
        },
        {
            "uuid": "11111111-2f05-4211-8eb4-a03b01a047a5",
            "valid_from": "2023-01-01",
            "valid_to": "2024-01-01",
            "created_at": "2023-01-01T00:00:00+00:00",
            "owner_type": school_1.type_,
            "owner_level": school_1.level,
            "owner_eids": [school_1.eid],
            "is_trial": False,
            "nof_seats": 10,
            "nof_free_seats": 10,
            "nof_occupied_seats": 0,
            "extra_seats": 0,
            "product_eid": product_1_eid,
        },
    ]


@pytest.mark.asyncio
async def test_get_managed_licenses__ok_empty_hierarchies(
    client: AsyncClient,
    create_license,
    teacher_1_hierarchies_authorization_token_no_hierarchies,
    teacher_1,
    teacher_1_hierarchies,
    teacher_2,
    product_1_eid,
    class_1,
    school_1,
):
    await create_license(
        uuid="11111111-2f05-4211-8eb4-a03b01a047a5",
        owner_type=school_1.type_,
        owner_level=school_1.level,
        owner_eids=[school_1.eid],
    )

    response = await client.post(
        "/v1/hierarchy/licenses",
        json={"hierarchies": []},
        headers={
            "Authorization": f"Bearer {teacher_1_hierarchies_authorization_token_no_hierarchies}"
        },
    )
    assert response.status_code == http_status.HTTP_200_OK
    assert json.loads(response._content)["items"] == [
        {
            "uuid": "11111111-2f05-4211-8eb4-a03b01a047a5",
            "valid_from": "2023-01-01",
            "valid_to": "2024-01-01",
            "created_at": "2023-01-01T00:00:00+00:00",
            "owner_type": school_1.type_,
            "owner_level": school_1.level,
            "owner_eids": [school_1.eid],
            "is_trial": False,
            "nof_seats": 10,
            "nof_free_seats": 10,
            "nof_occupied_seats": 0,
            "extra_seats": 0,
            "product_eid": product_1_eid,
        },
    ]


@pytest.mark.asyncio
async def test_get_managed_licenses__error(
    client: AsyncClient,
    create_license,
    teacher_1_hierarchies_authorization_token_no_hierarchies,
    teacher_1,
    teacher_1_hierarchies,
    teacher_2,
    product_1_eid,
    class_1,
    school_1,
):
    await create_license(
        uuid="11111111-2f05-4211-8eb4-a03b01a047a5",
        owner_type=school_1.type_,
        owner_level=school_1.level,
        owner_eids=[school_1.eid],
    )

    response = await client.post(
        "/v1/hierarchy/licenses",
        json={"hierarchies": None},
        headers={
            "Authorization": f"Bearer {teacher_1_hierarchies_authorization_token_no_hierarchies}"
        },
    )
    assert response.status_code == http_status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
@freeze_time("2023-01-10")
async def test_get_valid_licenses__ok_self(
    client: AsyncClient,
    create_license,
    teacher_1_hierarchies_authorization_token,
    teacher_1_hierarchies,
    class_1,
):
    await create_license(uuid="11111111-aea8-4de2-bcca-7b1945285502")

    response = await client.put(
        "/v1/hierarchy/licenses/entity-licenses",
        json={
            "entity_type": class_1.type_,
            "entity_eid": class_1.eid,
            "hierarchies": teacher_1_hierarchies,
        },
        headers={
            "Authorization": f"Bearer {teacher_1_hierarchies_authorization_token}"
        },
    )
    assert response.status_code == http_status.HTTP_200_OK
    assert json.loads(response._content) == [
        {
            "uuid": "11111111-aea8-4de2-bcca-7b1945285502",
            "product_eid": "product_1",
            "valid_from": "2023-01-01",
            "valid_to": "2024-01-01",
            "owner_type": class_1.type_,
            "owner_level": class_1.level,
            "owner_eids": [class_1.eid],
            "extra_seats": 0,
            "nof_seats": 10,
            "nof_free_seats": 10,
            "nof_occupied_seats": 0,
            "is_trial": False,
        }
    ]


@pytest.mark.asyncio
@freeze_time("2023-01-10")
async def test_get_valid_licenses__ok_parent(
    client: AsyncClient,
    create_license,
    teacher_1_hierarchies_authorization_token,
    teacher_1_hierarchies,
    class_1,
    school_1,
):
    await create_license(
        uuid="11111111-aea8-4de2-bcca-7b1945285502",
        owner_type=school_1.type_,
        owner_level=school_1.level,
        owner_eids=[school_1.eid],
    )

    response = await client.put(
        "/v1/hierarchy/licenses/entity-licenses",
        json={
            "entity_type": class_1.type_,
            "entity_eid": class_1.eid,
            "hierarchies": teacher_1_hierarchies,
        },
        headers={
            "Authorization": f"Bearer {teacher_1_hierarchies_authorization_token}"
        },
    )
    assert response.status_code == http_status.HTTP_200_OK
    assert json.loads(response._content) == [
        {
            "uuid": "11111111-aea8-4de2-bcca-7b1945285502",
            "product_eid": "product_1",
            "valid_from": "2023-01-01",
            "valid_to": "2024-01-01",
            "owner_type": school_1.type_,
            "owner_level": school_1.level,
            "owner_eids": [school_1.eid],
            "nof_seats": 10,
            "extra_seats": 0,
            "nof_free_seats": 10,
            "nof_occupied_seats": 0,
            "is_trial": False,
        }
    ]


@pytest.mark.asyncio
@freeze_time("2023-01-10")
async def test_get_valid_licenses__ok_all_expired(
    client: AsyncClient,
    create_license,
    teacher_1_hierarchies_authorization_token,
    teacher_1_hierarchies,
    class_1,
):
    await create_license(
        uuid="11111111-aea8-4de2-bcca-7b1945285502",
        valid_to=datetime.date(2023, 1, 9),
    )
    response = await client.put(
        "/v1/hierarchy/licenses/entity-licenses",
        json={
            "entity_type": class_1.type_,
            "entity_eid": class_1.eid,
            "hierarchies": teacher_1_hierarchies,
        },
        headers={
            "Authorization": f"Bearer {teacher_1_hierarchies_authorization_token}"
        },
    )
    assert response.status_code == http_status.HTTP_200_OK
    assert json.loads(response._content) == []


@pytest.mark.asyncio
@freeze_time("2023-01-10")
async def test_get_valid_licenses__ok_no_free_seats_left(
    client: AsyncClient,
    create_license,
    teacher_1_hierarchies_authorization_token,
    teacher_1_hierarchies,
    class_1,
):
    await create_license(uuid="11111111-aea8-4de2-bcca-7b1945285502", nof_seats=0)
    response = await client.put(
        "/v1/hierarchy/licenses/entity-licenses",
        json={
            "entity_type": class_1.type_,
            "entity_eid": class_1.eid,
            "hierarchies": teacher_1_hierarchies,
        },
        headers={
            "Authorization": f"Bearer {teacher_1_hierarchies_authorization_token}"
        },
    )
    assert response.status_code == http_status.HTTP_200_OK
    assert json.loads(response._content) == []


@pytest.mark.asyncio
@freeze_time("2023-01-10")
async def test_get_valid_licenses__ok_infinite_seats_left(
    client: AsyncClient,
    create_license,
    teacher_1_hierarchies_authorization_token,
    teacher_1_hierarchies,
    class_1,
):
    # test case for 'infinity': nof_seats is -1
    await create_license(uuid="11111111-aea8-4de2-bcca-7b1945285502", nof_seats=-1)
    response = await client.put(
        "/v1/hierarchy/licenses/entity-licenses",
        json={
            "entity_type": class_1.type_,
            "entity_eid": class_1.eid,
            "hierarchies": teacher_1_hierarchies,
        },
        headers={
            "Authorization": f"Bearer {teacher_1_hierarchies_authorization_token}"
        },
    )
    assert response.status_code == http_status.HTTP_200_OK
    assert json.loads(response._content) == [
        {
            "uuid": "11111111-aea8-4de2-bcca-7b1945285502",
            "product_eid": "product_1",
            "valid_from": "2023-01-01",
            "valid_to": "2024-01-01",
            "owner_type": class_1.type_,
            "owner_level": class_1.level,
            "owner_eids": [class_1.eid],
            "nof_seats": -1,
            "extra_seats": 0,
            "nof_free_seats": -1,
            "nof_occupied_seats": 0,
            "is_trial": False,
        }
    ]


@pytest.mark.asyncio
@freeze_time("2023-01-10")
async def test_get_active_license__ok(
    client: AsyncClient,
    create_license,
    teacher_1_hierarchies_authorization_token,
    teacher_1_hierarchies,
    class_1,
    school_1,
):
    await create_license(
        uuid="11111111-aea8-4de2-bcca-7b1945285502",
        owner_type=school_1.type_,
        owner_level=school_1.level,
        owner_eids=[school_1.eid],
    )
    await create_license(
        uuid="22222222-aea8-4de2-bcca-7b1945285502",
    )
    response = await client.put(
        "/v1/hierarchy/licenses/entity-license",
        json={
            "entity_type": class_1.type_,
            "entity_eid": class_1.eid,
            "hierarchies": teacher_1_hierarchies,
        },
        headers={
            "Authorization": f"Bearer {teacher_1_hierarchies_authorization_token}"
        },
    )
    assert response.status_code == http_status.HTTP_200_OK
    assert json.loads(response._content) == {
        "uuid": "22222222-aea8-4de2-bcca-7b1945285502",
        "product_eid": "product_1",
        "valid_from": "2023-01-01",
        "valid_to": "2024-01-01",
        "owner_type": class_1.type_,
        "owner_level": class_1.level,
        "owner_eids": [class_1.eid],
        "nof_seats": 10,
        "nof_free_seats": 10,
        "nof_occupied_seats": 0,
        "extra_seats": 0,
        "is_trial": False,
    }


@pytest.mark.asyncio
@freeze_time("2023-01-10")
async def test_get_active_license__ok_no_result(
    client: AsyncClient,
    create_license,
    teacher_1_hierarchies_authorization_token,
    teacher_1_hierarchies,
    class_1,
):
    await create_license(
        uuid="11111111-aea8-4de2-bcca-7b1945285502",
        valid_from=datetime.date(2023, 1, 1),
        valid_to=datetime.date(2023, 1, 2),
    ),
    await create_license(
        uuid="22222222-aea8-4de2-bcca-7b1945285502",
        valid_from=datetime.date(2023, 1, 1),
        valid_to=datetime.date(2024, 1, 2),
        nof_seats=0,
    )
    response = await client.put(
        "/v1/hierarchy/licenses/entity-license",
        json={
            "entity_type": class_1.type_,
            "entity_eid": class_1.eid,
            "hierarchies": teacher_1_hierarchies,
        },
        headers={
            "Authorization": f"Bearer {teacher_1_hierarchies_authorization_token}"
        },
    )
    assert response.status_code == http_status.HTTP_200_OK
    assert json.loads(response._content) is None
