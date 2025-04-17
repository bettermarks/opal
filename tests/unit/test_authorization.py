import datetime
import json
import pytest
from unittest.mock import MagicMock
from httpx import AsyncClient
from fastapi import status as http_status


from tests.conftest import (
    create_token,
    NOT_EXISTING_KID,
    HIERARCHY_PROVIDER_KID,
    INVALID_SIGNATURE_KEY_KID,
)


#
# authorization tests ...
#


@pytest.mark.asyncio
async def test_authorization__401_invalid_auth_header(client: AsyncClient, caplog):
    """Authorization fails because of no token"""
    headers = {"Authorization": ""}
    response = await client.get("/route-that-expects-authorization", headers=headers)
    assert response.status_code == http_status.HTTP_401_UNAUTHORIZED
    assert caplog.records[0].levelname == "INFO"
    assert "API failure" in caplog.text
    assert "Invalid or missing authorization header" in caplog.text
    assert json.loads(response._content) == {
        "detail": "Invalid or missing authorization header"
    }


@pytest.mark.asyncio
async def test_authorization__401_invalid_schema(client: AsyncClient, caplog):
    """Authorization fails because of invalid token schema"""
    headers = {"Authorization": "something invalid"}
    response = await client.get("/route-that-expects-authorization", headers=headers)
    assert response.status_code == http_status.HTTP_401_UNAUTHORIZED
    assert caplog.records[0].levelname == "INFO"
    assert "API failure" in caplog.text
    assert "Invalid authorization scheme" in caplog.text
    assert json.loads(response._content) == {"detail": "Invalid authorization scheme"}


@pytest.mark.asyncio
async def test_authorization__401_invalid_token(client: AsyncClient, caplog):
    """Authorization fails because of invalid"""
    headers = {"Authorization": "Bearer"}
    response = await client.get("/route-that-expects-authorization", headers=headers)
    assert response.status_code == http_status.HTTP_401_UNAUTHORIZED
    assert caplog.records[0].levelname == "INFO"
    assert "API failure" in caplog.text
    assert "Invalid or missing authorization header" in caplog.text
    assert json.loads(response._content) == {
        "detail": "Invalid or missing authorization header"
    }


@pytest.mark.asyncio
async def test_authorization__401_kid_not_found(client: AsyncClient, caplog):
    """
    Requested hierarchy provider is not registered for authorization
    """
    token = create_token(
        NOT_EXISTING_KID,
        "some-issuer",
        (
            datetime.datetime.now(tz=datetime.timezone.utc)
            + datetime.timedelta(seconds=100)
        ).timestamp(),
        "some-subject",
    )

    response = await client.get(
        "/route-that-expects-authorization",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == http_status.HTTP_401_UNAUTHORIZED
    assert caplog.records[0].levelname == "INFO"
    assert "API failure" in caplog.text
    assert "Key ID (kid) cannot be identified" in caplog.text
    assert json.loads(response._content) == {
        "detail": f"Key ID (kid) cannot be identified: {{'kid': '{NOT_EXISTING_KID}'}}"
    }


@pytest.mark.asyncio
async def test_authorization__401_token_expired(client: AsyncClient, caplog):
    """
    token is expired
    """
    token = create_token(
        HIERARCHY_PROVIDER_KID,
        "some-issuer",
        (
            datetime.datetime.now(tz=datetime.timezone.utc)
            - datetime.timedelta(seconds=100)
        ).timestamp(),
        "some-subject",
    )

    response = await client.get(
        "/route-that-expects-authorization",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == http_status.HTTP_401_UNAUTHORIZED
    assert caplog.records[0].levelname == "INFO"
    assert "API failure" in caplog.text
    assert "JWT token validation failed" in caplog.text
    assert "Expired" in json.loads(response._content)["detail"]


@pytest.mark.asyncio
async def test_authorization__401_invalid_signature(client: AsyncClient, caplog):
    """
    token invalid signature
    """
    token = create_token(
        INVALID_SIGNATURE_KEY_KID,
        "some-issuer",
        (
            datetime.datetime.now(tz=datetime.timezone.utc)
            + datetime.timedelta(seconds=100)
        ).timestamp(),
        "some-subject",
    )

    response = await client.get(
        "/route-that-expects-authorization",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == http_status.HTTP_401_UNAUTHORIZED
    assert caplog.records[0].levelname == "INFO"
    assert "API failure" in caplog.text
    assert "JWS token signature validation failed" in caplog.text


@pytest.mark.asyncio
async def test_authorization__ok(client: AsyncClient, mocker: MagicMock):
    """
    token valid
    """
    token = create_token(
        HIERARCHY_PROVIDER_KID,
        "some-issuer",
        (
            datetime.datetime.now(tz=datetime.timezone.utc)
            + datetime.timedelta(seconds=100)
        ).timestamp(),
        "some-subject",
    )

    response = await client.get(
        "/route-that-expects-authorization",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == http_status.HTTP_200_OK
