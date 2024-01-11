import os
from typing import Dict

from fastapi import APIRouter
from fastapi import status as http_status

from services.licensing import settings
from services.licensing.logging import LogLevel
from services.licensing import __version__


router = APIRouter()


@router.get("", status_code=http_status.HTTP_200_OK)
def get_status() -> Dict:
    if os.path.exists("./SHA.txt"):
        with open("./SHA.txt", "r") as f:
            sha = f.read().strip("\n")
    else:
        sha = "NO_GIT_SHA_FILE"

    return {
        "status": "OK",
        "debug": True if settings.log_level == LogLevel.DEBUG else False,
        "version": __version__,
        "git:sha": sha,
    }
