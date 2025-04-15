import asyncio
import pytest
import structlog
from httpx import AsyncClient, ASGITransport
from typing import Any, Generator, Tuple
from fastapi import Depends, FastAPI, status as http_status

from services.licensing.authorization import authorize_with_token


logger = structlog.stdlib.get_logger(__name__)


@pytest.fixture(scope="session")
def event_loop(request) -> Generator:  # noqa: indirect usage
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


async def start_app():
    app = FastAPI()
    return app


@pytest.fixture
async def app() -> FastAPI:
    yield await start_app()


@pytest.fixture
async def client(app: FastAPI) -> AsyncClient:
    from services.licensing.main import http_exception_handler
    from services.licensing.exceptions import HTTPException

    app.add_exception_handler(HTTPException, http_exception_handler)

    @app.get(
        "/route-that-expects-authorization",
        status_code=http_status.HTTP_200_OK,
    )
    async def route_1(
        data: Tuple[str, str, None] = Depends(authorize_with_token),
    ) -> Any:
        return {"message": "Hi"}

    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://test-server"
    ) as client:
        yield client
