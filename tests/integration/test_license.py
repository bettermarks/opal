import json

import pytest
from freezegun import freeze_time
from httpx import AsyncClient
from fastapi import status as http_status


@pytest.mark.asyncio
@freeze_time("2023-01-10")
async def test_get_managed_license_by_uuid__ok(
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
    await create_license(
        uuid="11111111-2f05-4211-8eb4-a03b01a047a5",
        owner_type=school_1.type_,
        owner_level=school_1.level,
        owner_eids=[school_1.eid],
    ),

    response = await client.post(
        "/v1/hierarchy/licenses/11111111-2f05-4211-8eb4-a03b01a047a5",
        json={"hierarchies": teacher_1_hierarchies},
        headers={
            "Authorization": f"Bearer {teacher_1_hierarchies_authorization_token}"
        },
    )
    assert response.status_code == http_status.HTTP_200_OK
    assert json.loads(response._content) == {
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
    }
