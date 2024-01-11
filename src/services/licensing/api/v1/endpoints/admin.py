import datetime
from dataclasses import asdict
from typing import Tuple, Any, Dict

import structlog
from fastapi import APIRouter, Depends, Query
from fastapi import status as http_status

from services.licensing.api.v1.schema.license import (
    LicenseCompleteSchema,
    LicenseUpdateSchema,
    LicenseCreateSchema,
    LicenseCreatedSchema,
)
from services.licensing.authorization import authorize_with_admin_token
from services.licensing.business.service import LicensingService
from services.licensing.constants import (
    ALLOWED_LICENSE_FILTER_RESTRICTIONS,
    ALLOWED_LICENSE_ORDER_BY_FIELDS,
)
from services.licensing.exceptions import DuplicateEntryException, HTTPException
from services.licensing.order_by import get_order_by_fields
from services.licensing.pagination import (
    CustomPage,
    get_pagination_parameters,
    paginate,
)
from services.licensing.settings import repository, transaction_manager

logger = structlog.stdlib.get_logger(__name__)
router = APIRouter()


@router.get("/licenses", status_code=http_status.HTTP_200_OK)
async def get_licenses(
    product_eid: str = Query(None),
    owner_type: str = Query(None),
    owner_level: int = Query(None),
    owner_eid: str = Query(None),
    manager_eid: str = Query(None),
    valid_from: datetime.date = Query(None),
    valid_to: datetime.date = Query(None),
    is_trial: bool = Query(None),
    is_valid: bool = Query(None),
    created_at: datetime.date = Query(None),
    redeemed_seats: int = Query(None),
    order_by: str = Query(None),
    token_data: Tuple[str, Dict[str, Any]] = Depends(authorize_with_admin_token),
) -> CustomPage[LicenseCompleteSchema]:
    """
    The "get licenses" route for admins
    :param product_eid
    :param owner_type
    :param owner_level
    :param owner_eid
    :param manager_eid
    :param valid_from
    :param valid_to
    :param is_trial
    :param is_valid
    :param created_at
    :param redeemed_seats: 'percentage of occupied seats - filter
    :param order_by something like "-id.valid_from.-manager_eid.-product_eid
    :param token_data
    :return: a JSON object (usually a list of licenses)
    """
    _, payload = token_data
    page, page_size = get_pagination_parameters()

    async with transaction_manager() as tm:
        repo = repository(tm.session)
        licenses, total = await LicensingService(repo).get_licenses_paginated(
            page,
            page_size,
            get_order_by_fields(order_by, ALLOWED_LICENSE_ORDER_BY_FIELDS),
            payload["filter_restrictions"],
            ALLOWED_LICENSE_FILTER_RESTRICTIONS,
            product_eid=product_eid,
            owner_type=owner_type,
            owner_level=owner_level,
            owner_eid=owner_eid,
            manager_eid=manager_eid,
            valid_from=valid_from,
            valid_to=valid_to,
            is_trial=is_trial,
            created_at=created_at,
            is_valid=is_valid,
            redeemed_seats=redeemed_seats,
        )
        items = [LicenseCompleteSchema.parse_obj(asdict(l_)) for l_ in licenses]
        return paginate(items, page, page_size, total)


@router.post("/licenses", status_code=http_status.HTTP_201_CREATED)
async def create_license(
    data: LicenseCreateSchema,
    _: Tuple[str, Dict[str, Any]] = Depends(authorize_with_admin_token),
) -> LicenseCreatedSchema:
    """
    The 'create a license' route for use in administrative procedures.
    :param data: entity attributes dictionary for a license creation
    :param _: info gotten from ordering token (not used, but necessary)
    :returns: some params of the created license or some error
              message in case of an error
    """
    async with transaction_manager() as tm:
        license_ = await LicensingService(repository(tm.session)).create_license(
            hierarchy_provider_uri=data.hierarchy_provider_uri,
            manager_eid=data.manager_eid,
            product_eid=data.product_eid,
            owner_type=data.owner_type,
            owner_level=data.owner_level,
            owner_eids=data.owner_eids,
            valid_from=data.valid_from,
            valid_to=data.valid_to,
            nof_seats=data.nof_seats,
            extra_seats=data.extra_seats,
            notes=data.notes,
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
                    "License creation failed: "
                    "A license for at least one of the entered owner EIDs "
                    "already exists"
                ),
            )
        return LicenseCreatedSchema.parse_obj(license_) if license_ else None


@router.get("/licenses/{license_uuid}", status_code=http_status.HTTP_200_OK)
async def get_license(
    license_uuid: str,
    token_data: Tuple[str, Dict[str, Any]] = Depends(authorize_with_admin_token),
) -> LicenseCompleteSchema | None:
    """
    The "get details for a specific license" route for admins
    :param license_uuid: the `uuid` of the `License` entity to be selected as the result
    :param token_data: data gotten from admin token
    :return: a JSON object representing the license details
    """
    _, payload = token_data
    async with transaction_manager() as tm:
        license_ = await LicensingService(repository(tm.session)).get_license(
            license_uuid,
            payload["filter_restrictions"],
            ALLOWED_LICENSE_FILTER_RESTRICTIONS,
        )
        return LicenseCompleteSchema.parse_obj(asdict(license_)) if license_ else None


@router.put("/licenses/{license_uuid}", status_code=http_status.HTTP_200_OK)
async def update_license(
    license_uuid: str,
    license_update: LicenseUpdateSchema,
    token_data: Tuple[str, Dict[str, Any]] = Depends(authorize_with_admin_token),
) -> None:
    """
    The update license route for admins.
    :param license_uuid: the `uuid` of the license to modify
    :param license_update: the data to update the license with
    :param token_data: data gotten from admin token
    """
    _, payload = token_data
    async with transaction_manager(implicit_commit=True) as tm:
        await LicensingService(repository(tm.session)).update_license(
            license_uuid,
            payload["filter_restrictions"],
            **license_update.dict(exclude_unset=True)
        )
