import functools
import os

from fastapi import APIRouter
from fastapi import status as http_status

from services.licensing import settings
from services.licensing.business.service import LicensingService
from services.licensing.exceptions import HTTPException
from services.licensing.logging import LogLevel
from services.licensing import __version__
from services.licensing.settings import transaction_manager, repository

router = APIRouter()


@router.get("/livez", status_code=http_status.HTTP_200_OK)
async def get_livez() -> dict:
    return {
        "status": "OK",
    }


@router.get("/status", status_code=http_status.HTTP_200_OK)
async def get_status() -> dict:
    async with transaction_manager() as tm:
        if await LicensingService(repository(tm.session)).is_db_alive():
            return {"status": "OK"}
    raise HTTPException(
        status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
        message="Database not reachable",
    )


@router.get("/version", status_code=http_status.HTTP_200_OK)
async def get_version() -> dict:
    return {
        "debug": True if settings.log_level == LogLevel.DEBUG else False,
        "version": __version__,
        "git:sha": get_version_sha(),
        "segment": settings.segment,
    }


@functools.cache
def get_version_sha():
    if os.path.exists("./SHA.txt"):
        with open("./SHA.txt", "r") as f:
            sha = f.read().strip("\n")
    else:
        sha = "NO_GIT_SHA_FILE"
    return sha
