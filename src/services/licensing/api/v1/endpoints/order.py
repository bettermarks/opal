import structlog
from typing import Any, Tuple, Dict

from fastapi import APIRouter, Depends, status as http_status

from services.licensing.api.v1.schema.license import (
    LicenseCreatedSchema,
    LicensePurchaseSchema,
)
from services.licensing.authorization import authorize_with_shop_token
from services.licensing.exceptions import DuplicateEntryException, HTTPException
from services.licensing.business.service import LicensingService
from services.licensing.settings import repository, transaction_manager

logger = structlog.stdlib.get_logger(__name__)
router = APIRouter()


@router.post("/licenses", status_code=http_status.HTTP_201_CREATED)
async def purchase_license(
    token_data: Tuple[str, Dict[str, Any]] = Depends(authorize_with_shop_token),
) -> LicenseCreatedSchema:
    """
    The 'purchase a license' route
    :param token_data: info gotten from ordering token
    :returns: some params of the created license or some error
              message in case of an error
    """
    _, payload = token_data
    data = LicensePurchaseSchema(**payload["order"])

    async with transaction_manager() as tm:
        license_ = await LicensingService(repository(tm.session)).create_license(
            hierarchy_provider_uri=data.hierarchy_provider_uri,
            manager_eid=payload["sub"],
            product_eid=data.product_eid,
            owner_type=data.owner_type,
            owner_level=data.owner_level,
            owner_eids=data.owner_eids,
            valid_from=data.valid_from,
            valid_to=data.valid_to,
            nof_seats=data.nof_seats,
            extra_seats=data.extra_seats,
            order_id=data.order_id,
            is_trial=False,
        )
        try:
            await tm.commit()
            logger.info(
                "Successfully created license",
                is_trial=False,
                uuid=license_["uuid"],
                product=license_["product_eid"],
                owner_type=license_["owner_type"],
                nof_seats=license_["nof_seats"],
            )
        except DuplicateEntryException:
            raise HTTPException(
                status_code=http_status.HTTP_409_CONFLICT,
                message=(
                    "License purchase failed: "
                    "A license for at least one of the entered owner EIDs "
                    "already exists"
                ),
            )
    return license_
