import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_livez__ok(client: AsyncClient):
    response = await client.get("/livez")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_status__ok(client: AsyncClient):
    response = await client.get("/status")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_status__not_ok(mocker, client: AsyncClient):
    mocker.patch(
        "services.licensing.business.service.LicensingService.is_db_alive",
        return_value=False,
    )
    response = await client.get("/status")
    assert response.status_code == 500
    assert response.json() == {"detail": "Database not reachable"}


@pytest.mark.asyncio
async def test_version__ok(client: AsyncClient):
    response = await client.get("/version")
    assert response.status_code == 200
    assert response.json()["debug"] is True
    assert response.json()["segment"] == "loc00"
