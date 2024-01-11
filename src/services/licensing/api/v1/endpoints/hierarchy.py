from fastapi import APIRouter, Depends, Query, status as http_status, Body
from dataclasses import asdict
from typing import List, Dict, Any, Tuple

from services.licensing.api.v1.schema.hierarchy import HierarchiesSchema
from services.licensing.api.v1.schema.license import (
    LicenseActiveSchema,
    LicenseManagedSchema,
    LicenseValidSchema,
)
from services.licensing.api.v1.schema.entity import EntitySchema
from services.licensing.authorization import authorize_with_hierarchies_token
from services.licensing.business.service import LicensingService

# TODO: currently not used, but will be used when reactivating 'callback urls'
# from services.licensing.client import post_request
from services.licensing.constants import ALLOWED_LICENSE_ORDER_BY_FIELDS
from services.licensing.hierarchies import parent_entities
from services.licensing.order_by import get_order_by_fields
from services.licensing.pagination import (
    CustomPage,
    get_pagination_parameters,
    paginate,
)
from services.licensing.settings import repository, transaction_manager

router = APIRouter()


# TODO: currently not used, but will be used when reactivating 'callback urls'
# async def get_hierarchies(token: str, token_payload: Dict[str, Any]):
#     """
#     helper: gets hierarchies by calling back the hierarchy provider ...
#     :param token: the hierarchies token
#     :param token_payload: the payload from the hierarchies token ...
#     :return:
#     """
#     return parent_entities(
#         await get_request(token_payload["callback_url"], token), {}
#     )


@router.post("/licenses", status_code=http_status.HTTP_200_OK)
async def get_managed_licenses(
    _: HierarchiesSchema = Body(default_factory=HierarchiesSchema),
    order_by: str = Query(None),
    token_data: Tuple[str, Dict[str, Any]] = Depends(authorize_with_hierarchies_token),
) -> CustomPage[LicenseManagedSchema]:
    """
    All licenses in the hierarchy of a given user that they are managing / have created.

    ### Example Bearer Token structure
    ```
    {
        "iss": "https://acc.bettermarks.com/ucm",
        "exp": 1701789570.99798,
        "sub": "12@EN_test",
        "iat": 1701788970.99799,
        "jti": "2b47ca46-28b9-4b8d-bd1c-a893acb9de29",
        "hashes": {
            "memberships": {
                "alg": "SHA256",
                "hash": "86f8b8313c183b3f9ee74b9c042ee440b894f690e9f6308de3da63fd4a6b8"
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

    async with transaction_manager() as tm:
        licenses, total = await LicensingService(
            repository(tm.session)
        ).get_managed_licenses_paginated(
            page,
            page_size,
            get_order_by_fields(order_by, ALLOWED_LICENSE_ORDER_BY_FIELDS),
            payload["iss"],
            payload["sub"],
        )
        items = [LicenseManagedSchema.parse_obj(asdict(l_)) for l_ in licenses]
        return paginate(items, page, page_size, total)


@router.put("/licenses/entity-license", status_code=http_status.HTTP_200_OK)
async def get_active_license_for_entity(
    data: EntitySchema,
    token_data: Tuple[str, Dict[str, Any]] = Depends(authorize_with_hierarchies_token),
) -> LicenseActiveSchema | None:
    """
    The "active license for entity" route for a given entity, that is
    the license taken from the set of 'valid' licenses (see above route
    `/{entity_type}/{entity_eid}/valid-licenses`), that has the
    - minimum owner level
    - (for same owner level) maximum number of free seats

    ### Example Bearer Token structure
    ```
    {
        "iss": "https://acc.bettermarks.com/ucm",
        "exp": 1701789570.99798,
        "sub": "12@EN_test",
        "iat": 1701788970.99799,
        "jti": "2b47ca46-28b9-4b8d-bd1c-a893acb9de29",
        "hashes": {
            "memberships": {
                "alg": "SHA256",
                "hash": "86f8b8313c183b3f9ee74b9c042ee440b894f690e9f6308de3da63fd4a6b8"
            }
        }
    }
    ```
    \f
    :param data: entity eid, type, etc.
    :param token_data: data gotten from hierarchies token
    :return: a JSON object (usually a list of licenses)
    """
    _, payload = token_data
    # TODO: create Entity instances when serializing
    hierarchies = parent_entities(data.hierarchies, {})

    async with transaction_manager() as tm:
        active_license = await LicensingService(
            repository(tm.session)
        ).get_active_license_for_entity_tree(
            payload["iss"], data.entity_type, data.entity_eid, hierarchies
        )
        return (
            LicenseActiveSchema.parse_obj(asdict(active_license))
            if active_license
            else None
        )


@router.put("/licenses/entity-licenses", status_code=http_status.HTTP_200_OK)
async def get_licenses_for_entity(
    data: EntitySchema,
    token_data: Tuple[str, Dict[str, Any]] = Depends(authorize_with_hierarchies_token),
) -> List[LicenseValidSchema]:
    """
    The "valid licenses for entity" route for a given entity, that is
    'all licenses, that are currently not expired and that are owned by
    some ancestor of a given entity or by the entity itself'.
    \f
    :param data: entity eid, type, etc.
    :param token_data: data gotten from hierarchies token
    :return: a JSON object (usually a list of licenses)
    """
    _, payload = token_data
    # TODO: create Entity instances when serializing
    hierarchies = parent_entities(data.hierarchies, {})

    async with transaction_manager() as tm:
        return [
            LicenseValidSchema.parse_obj(asdict(l_))
            for l_ in await LicensingService(
                repository(tm.session)
            ).get_valid_licenses_for_entity_tree(
                payload["iss"], data.entity_type, data.entity_eid, hierarchies
            )
        ]
