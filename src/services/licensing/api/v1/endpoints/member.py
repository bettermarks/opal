import datetime
import structlog
from typing import Tuple, Dict, Any
from dataclasses import asdict
from dateutil.relativedelta import relativedelta

from fastapi import APIRouter, Depends, Body, Query
from fastapi import status as http_status

from services.licensing import settings
from services.licensing.authorization import (
    authorize_with_memberships_token,
)
from services.licensing.api.v1.schema.license import (
    LicenseCreatedSchema,
    LicenseTrialSchema,
    LicenseAvailableSchema,
)
from services.licensing.api.v1.schema.member import MembershipsSchema

# TODO: currently not used, but will be used when reactivating 'callback urls'
# from services.licensing.client import post_request
from services.licensing.business.service import LicensingService
from services.licensing.constants import ALLOWED_LICENSE_ORDER_BY_FIELDS
from services.licensing.custom_types import Entity
from services.licensing.exceptions import DuplicateEntryException, HTTPException
from services.licensing.order_by import get_order_by_fields
from services.licensing.pagination import (
    CustomPage,
    get_pagination_parameters,
    paginate,
)
from services.licensing.settings import transaction_manager, repository
from services.licensing.tokens import get_expiration_timestamp, create_licensing_token

logger = structlog.stdlib.get_logger(__name__)
router = APIRouter()


# TODO: currently not used, but will be used when reactivating 'callback urls'
# async def get_memberships(token: str, token_payload: Dict[str, Any]):
#     return [
#         Entity(
#             type_=m["type"],
#             eid=m["eid"],
#             level=m.get("level"),
#             name=m.get("name")
#         )
#         for m in await get_request(token_payload["callback_url"], token)
#     ]


@router.post("/permissions", status_code=http_status.HTTP_200_OK)
async def get_accessible_products(
    data: MembershipsSchema,
    token_data: Tuple[str, Dict[str, Any]] = Depends(authorize_with_memberships_token),
) -> str:
    """
    The "permission" route for a given user
    :param data: a membership data structure used to get the permissions for
    :param token_data: info gotten from memberships token
    :return: a JSON object (usually a list of accessible product EIDs)
    """
    token, payload = token_data
    memberships = [
        Entity(type_=m["type"], eid=m["eid"], level=m.get("level"), name=m.get("name"))
        for m in data.memberships
    ]
    # todo: deprecated due to a change of an approach
    # memberships = await get_memberships(token, payload)

    async with transaction_manager() as tm:
        accessible_products = await LicensingService(
            repository(tm.session)
        ).get_accessible_products(payload["iss"], payload["sub"], memberships)
        await tm.commit()

    return create_licensing_token(
        {
            "iss": settings.licensing_service_url,
            "exp": get_expiration_timestamp(settings.permissions_token_livetime_secs),
            "sub": payload["sub"],
            "accessible_products": accessible_products,
            "hierarchy_provider_uri": payload["iss"],
        }
    )


@router.post(
    "/licenses/trial",
    status_code=http_status.HTTP_201_CREATED,
    responses={
        409: {
            "description": "Duplicate Error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": (
                            "Trial license creation failed:"
                            " A trial license for this entity already exists"
                        ),
                    },
                },
            },
        },
    },
)
async def create_trial_license(
    data: LicenseTrialSchema,
    token_data: Tuple[str, Dict[str, Any]] = Depends(authorize_with_memberships_token),
) -> LicenseCreatedSchema:
    """
    The 'create a trial license route
    :param data: payload
    :param token_data: info gotten from memberships token
    :returns: some params of the created license or some error
              message in case of an error
    """
    _, payload = token_data

    valid_from = datetime.datetime.utcnow().date()
    valid_to = valid_from + relativedelta(
        weeks=data.duration_weeks or settings.trial_license_weeks
    )
    # TODO: create Entity instances when serializing
    memberships = [
        Entity(type_=m["type"], eid=m["eid"], level=m.get("level"), name=m.get("name"))
        for m in data.memberships
    ]

    # Do the actual check, if the owner EID is part of the memberships.
    if Entity(type_=data.owner_type, eid=data.owner_eid) not in memberships:
        logger.warn(
            "license owner does not match any users membership",
            owner_type=data.owner_type,
            owner_eid=data.owner_eid,
        )
        raise HTTPException(
            status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY,
            message=(
                "License creation failed: "
                "license owner does not match any users membership"
            ),
        )

    async with transaction_manager() as tm:
        valid_licenses = await LicensingService(
            repository(tm.session)
        ).get_valid_licenses_for_entity(
            hierarchy_provider_uri=payload["iss"],
            entity_type=data.owner_type,
            entity_eid=data.owner_eid,
        )
        if [
            lic
            for lic in valid_licenses
            if lic.product_eid == data.product_eid and lic.is_trial
        ]:
            raise HTTPException(
                status_code=http_status.HTTP_409_CONFLICT,
                message=(
                    "Trial license creation failed: "
                    "A trial license for this entity already exists"
                ),
            )
        license_dict = await LicensingService(repository(tm.session)).create_license(
            hierarchy_provider_uri=payload["iss"],
            manager_eid=payload["sub"],
            product_eid=data.product_eid,
            owner_type=data.owner_type,
            owner_level=data.owner_level,
            owner_eids=[data.owner_eid],
            valid_from=valid_from,
            valid_to=valid_to,
            nof_seats=data.nof_seats,
            extra_seats=data.extra_seats,
            is_trial=True,
        )
        try:
            await tm.commit()
            logger.info(
                "Successfully created license",
                is_trial=True,
                uuid=license_dict["uuid"],
                product=license_dict["product_eid"],
                owner_type=license_dict["owner_type"],
                nof_seats=license_dict["nof_seats"],
            )
        except DuplicateEntryException:
            raise HTTPException(
                status_code=http_status.HTTP_409_CONFLICT,
                message=(
                    "Trial license creation failed: "
                    "A license with these properties already exists"
                ),
            )
    return LicenseCreatedSchema.parse_obj(license_dict)


@router.post("/licenses", status_code=http_status.HTTP_200_OK)
async def get_available_licenses(
    data: MembershipsSchema = Body(default_factory=MembershipsSchema),
    order_by: str = Query(None),
    token_data: Tuple[str, Dict[str, Any]] = Depends(authorize_with_memberships_token),
) -> CustomPage[LicenseAvailableSchema]:
    """
    Route for getting all licenses that are available in the entities a given user is
    member of.

    ### Example Bearer Token structure
    ```
    {
        "iss": "https://acc.bettermarks.com/ucm",
        "exp": 1701799583.393268,
        "sub": "3@DE_bettermarks",
        "iat": 1701798983.393283,
        "jti": "77ab5b01-83a0-44f3-a086-d25162aae84e",
        "hashes": {
            "memberships": {
            "alg": "SHA256",
            "hash": "4c8c51dd16136b9905908bc3b6b938067e002e4345679c950abf86a3e2ce05ce"
            }
        }
        }
    ```
    \f
    :param _: a list of hierarchies of a user (is not used right now)
    :param order_by something like "-id.valid_from.-manager_eid.-product_eid
    :param token_data: info gotten from hierarchies token
    :return: a JSON object (usually a list of accessible product EIDs)
    """
    _, payload = token_data
    page, page_size = get_pagination_parameters()

    memberships = [
        Entity(type_=m["type"], eid=m["eid"], level=m.get("level"), name=m.get("name"))
        for m in data.memberships
    ]

    async with transaction_manager() as tm:
        licenses, total = await LicensingService(
            repository(tm.session)
        ).get_licenses_for_entities_paginated(
            page,
            page_size,
            get_order_by_fields(order_by, ALLOWED_LICENSE_ORDER_BY_FIELDS),
            payload["iss"],
            memberships,
        )
        items = [LicenseAvailableSchema.parse_obj(asdict(l_)) for l_ in licenses]
        return paginate(items, page, page_size, total)
