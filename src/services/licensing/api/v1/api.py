from fastapi import APIRouter

from services.licensing.api.v1.endpoints import (
    admin,
    hierarchy,
    member,
    status,
    order,
    shop,
)

api_router = APIRouter()

api_router.include_router(admin.router, prefix="/admin", tags=["Admin"])
api_router.include_router(status.router, prefix="/status", tags=["Status"])
api_router.include_router(member.router, prefix="/member", tags=["Member"])
api_router.include_router(hierarchy.router, prefix="/hierarchy", tags=["Hierarchy"])
api_router.include_router(order.router, prefix="/order", tags=["Order"])
