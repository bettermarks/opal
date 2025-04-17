import json
import asyncio
import datetime

import structlog

from hashlib import sha256
from typing import Generator

import pytest

from fastapi import FastAPI
from fastapi_pagination import add_pagination
from httpx import AsyncClient, ASGITransport
from jwcrypto import jwt

from services.licensing.api import endpoints
from services.licensing.api.v1.api import api_router
from services.licensing import settings
from services.licensing.business.service import LicensingService
from services.licensing.custom_types import Entity, SeatStatus, License
from services.licensing.data.sqlalchemy.unit_of_work import postgres_dsn
from services.licensing.main import ROUTE_PREFIX
from services.licensing.settings import transaction_manager, repository
from services.licensing.tokens import get_key_from_pem
from tests.conftest import (
    create_token,
    SHOP_SERVICE_KID,
    HIERARCHY_PROVIDER_KID,
    BACKOFFICE_KID,
    TEST_LICENSING_SERVICE_EC256_PUBLIC_KEY,
)


# we need to import all models here to set up the database ...
# Please do not remove the following 3 imports!!
from services.licensing.data.sqlalchemy.model.license import LicenseModel
from services.licensing.data.sqlalchemy.model.seat import SeatModel
from services.licensing.data.sqlalchemy.model.event_log import EventLogModel

# Please do not remove that import!!
from services.licensing.data.sqlalchemy.model.base import Model

logger = structlog.stdlib.get_logger(__name__)


TEST_DATABASE_DSN = postgres_dsn(
    settings.db_host,
    settings.db_port,
    settings.db_user,
    settings.db_password,
    "test_licensing",
)


# we need that for setting up the DB tables ...
target_metadata = Model.metadata


def hashed_payload(payload_key, payload):
    """helper: hashes some payload and returns the hash using some predefined structure"""
    return {
        "hashes": {
            f"{payload_key}": {
                "alg": "SHA256",
                "hash": sha256(json.dumps(payload).encode("utf-8")).hexdigest(),
            }
        }
    }


def check_license_service_token(token):
    # deserialize nested token without decryption to get kid ...
    jws_token = jwt.JWS()
    jws_token.deserialize(token)
    jws_kid = jws_token.jose_header["kid"]
    assert jws_kid == settings.licensing_service_kid
    jwt_token = jwt.JWT(
        key=get_key_from_pem(TEST_LICENSING_SERVICE_EC256_PUBLIC_KEY.encode("utf-8")),
        jwt=token,
    )
    return json.loads(jwt_token.claims)


@pytest.fixture
def teacher_1() -> Entity:
    return Entity(type_="teacher", eid="teacher_1@DE_bettermarks", level=0)


@pytest.fixture
def teacher_2() -> Entity:
    return Entity(type_="teacher", eid="teacher_2@CH_bettermarks", level=0)


@pytest.fixture
def teacher_no_class_2() -> Entity:
    return Entity(type_="teacher", eid="teacher_no_class_2", level=0)


@pytest.fixture
def student_1() -> Entity:
    return Entity(type_="student", eid="student_1@DE_bettermarks", level=0)


@pytest.fixture
def student_2() -> Entity:
    return Entity(type_="student", eid="student_2@CH_bettermarks", level=0)


@pytest.fixture
def student_3() -> Entity:
    return Entity(type_="student", eid="student_3@DE_bettermarks", level=0)


@pytest.fixture
def class_1() -> Entity:
    return Entity(type_="class", eid="class_1@DE_bettermarks", level=1)


@pytest.fixture
def class_2() -> Entity:
    return Entity(type_="class", eid="class_2@CH_bettermarks", level=1)


@pytest.fixture
def school_1() -> Entity:
    return Entity(type_="school", eid="school_1@DE_bettermarks", level=2)


@pytest.fixture
def school_2() -> Entity:
    return Entity(type_="school", eid="school_2@CH_bettermarks", level=2)


@pytest.fixture
def state_1() -> Entity:
    return Entity(type_="state", eid="DE-RP@DE_bettermarks", level=2)


@pytest.fixture
def hierarchy_provider_1_uri() -> str:
    return "http://example_hierarchy_provider.com"


@pytest.fixture
def shop_service_1_url() -> str:
    return "http://example_shop_service.com"


@pytest.fixture
def backoffice_1_uri() -> str:
    return "http://example_backoffice.com"


@pytest.fixture
def product_1_eid() -> str:
    return "product_1"


@pytest.fixture
def product_2_eid() -> str:
    return "product_2"


@pytest.fixture
def admin_1_eid() -> str:
    return "admin_1"


@pytest.fixture
def teacher_1_purchase_payload(
    hierarchy_provider_1_uri, product_1_eid, class_1, class_2
) -> dict:
    return {
        "hierarchy_provider_uri": hierarchy_provider_1_uri,
        "owner_type": class_1.type_,
        "owner_level": class_1.level,
        "owner_eids": [class_1.eid, class_2.eid],
        "valid_from": "2023-02-10",
        "valid_to": "2024-02-10",
        "nof_seats": 100,
        "extra_seats": 0,
        "product_eid": product_1_eid,
    }


@pytest.fixture
def teacher_1_purchase_payload_state_license(
    hierarchy_provider_1_uri, product_1_eid, class_1, class_2
) -> dict:
    """
    This is a fixture that supposed to crash requests, because of `owner_type`.
    Teacher role shouldn't be able to purchase federal state licenses.
    """
    return {
        "hierarchy_provider_uri": hierarchy_provider_1_uri,
        "owner_type": "state",
        "owner_level": 10,
        "owner_eids": [class_1.eid, class_2.eid],
        "valid_from": "2023-02-10",
        "valid_to": "2024-02-10",
        "nof_seats": 100,
        "extra_seats": 0,
        "product_eid": product_1_eid,
    }


@pytest.fixture
def teacher_1_trial_payload(product_1_eid, class_1) -> dict:
    return {
        "owner_type": class_1.type_,
        "owner_level": class_1.level,
        "owner_eid": class_1.eid,
        "nof_seats": 50,
        "product_eid": product_1_eid,
    }


@pytest.fixture
def teacher_1_shop_authorization_token(
    teacher_1,
    shop_service_1_url,
    teacher_1_purchase_payload,
):
    return create_token(
        SHOP_SERVICE_KID,
        shop_service_1_url,
        (
            datetime.datetime.now(tz=datetime.timezone.utc)
            + datetime.timedelta(seconds=100)
        ).timestamp(),
        teacher_1.eid,
        {"order": teacher_1_purchase_payload},
    )


@pytest.fixture
def teacher_1_shop_authorization_token_state_license(
    teacher_1,
    shop_service_1_url,
    teacher_1_purchase_payload_state_license,
) -> str:
    """
    This fixture represents standard shop token, except the fact that
    `owner_type` is `state` (federal state license, which is prohibited
    to purchase by teachers.
    """
    return create_token(
        SHOP_SERVICE_KID,
        shop_service_1_url,
        (
            datetime.datetime.now(tz=datetime.timezone.utc)
            + datetime.timedelta(seconds=100)
        ).timestamp(),
        teacher_1.eid,
        {"order": teacher_1_purchase_payload_state_license},
    )


@pytest.fixture
def teacher_1_memberships(teacher_1, class_1, class_2):
    return [
        {"type": class_1.type_, "level": class_1.level, "eid": class_1.eid},
        {"type": class_2.type_, "level": class_2.level, "eid": class_2.eid},
    ]


@pytest.fixture
def teacher_1_memberships_authorization_token(
    teacher_1, class_1, class_2, hierarchy_provider_1_uri, teacher_1_memberships
):
    return create_token(
        HIERARCHY_PROVIDER_KID,
        hierarchy_provider_1_uri,
        (
            datetime.datetime.now(tz=datetime.timezone.utc)
            + datetime.timedelta(seconds=100)
        ).timestamp(),
        teacher_1.eid,
        hashed_payload("memberships", teacher_1_memberships),
    )


@pytest.fixture
def teacher_1_hierarchies(teacher_1, class_1, school_1, state_1):
    return [
        {
            "eid": state_1.eid,
            "type": state_1.type_,
            "name": "Rheinland-Pfalz",
            "level": state_1.level,
            "children": [
                {
                    "eid": school_1.eid,
                    "type": school_1.type_,
                    "name": "school 1",
                    "level": school_1.level,
                    "children": [
                        {
                            "eid": class_1.eid,
                            "type": class_1.type_,
                            "name": class_1.level,
                            "level": 1,
                        },
                    ],
                }
            ],
        }
    ]


@pytest.fixture
def teacher_1_hierarchies_authorization_token(
    teacher_1, class_1, school_1, hierarchy_provider_1_uri, teacher_1_hierarchies
):
    return create_token(
        HIERARCHY_PROVIDER_KID,
        hierarchy_provider_1_uri,
        (
            datetime.datetime.now(tz=datetime.timezone.utc)
            + datetime.timedelta(seconds=100)
        ).timestamp(),
        teacher_1.eid,
        hashed_payload("hierarchies", teacher_1_hierarchies),
    )


@pytest.fixture
def teacher_1_hierarchies_authorization_token_no_hierarchies(
    teacher_1, class_1, school_1, hierarchy_provider_1_uri, teacher_1_hierarchies
):
    return create_token(
        HIERARCHY_PROVIDER_KID,
        hierarchy_provider_1_uri,
        (
            datetime.datetime.now(tz=datetime.timezone.utc)
            + datetime.timedelta(seconds=100)
        ).timestamp(),
        teacher_1.eid,
        hashed_payload("hierarchies", []),
    )


@pytest.fixture
def student_1_class_1_memberships(student_1, class_1):
    return [
        {"type": class_1.type_, "level": class_1.level, "eid": class_1.eid},
    ]


@pytest.fixture
def student_1_class_1_memberships_authorization_token(
    student_1, hierarchy_provider_1_uri, student_1_class_1_memberships
):
    return create_token(
        HIERARCHY_PROVIDER_KID,
        hierarchy_provider_1_uri,
        (
            datetime.datetime.now(tz=datetime.timezone.utc)
            + datetime.timedelta(seconds=100)
        ).timestamp(),
        student_1.eid,
        hashed_payload("memberships", student_1_class_1_memberships),
    )


@pytest.fixture
def student_1_class_2_memberships(student_1, class_2):
    return [
        {"type": class_2.type_, "level": class_2.level, "eid": class_2.eid},
    ]


@pytest.fixture
def student_1_class_2_memberships_authorization_token(
    student_1, hierarchy_provider_1_uri, student_1_class_2_memberships
):
    return create_token(
        HIERARCHY_PROVIDER_KID,
        hierarchy_provider_1_uri,
        (
            datetime.datetime.now(tz=datetime.timezone.utc)
            + datetime.timedelta(seconds=100)
        ).timestamp(),
        student_1.eid,
        hashed_payload("memberships", student_1_class_2_memberships),
    )


@pytest.fixture
def student_2_class_1_memberships(student_2, class_1):
    return [
        {"type": class_1.type_, "level": class_1.level, "eid": class_1.eid},
    ]


@pytest.fixture
def student_2_class_1_memberships_authorization_token(
    student_2, hierarchy_provider_1_uri, student_2_class_1_memberships
):
    return create_token(
        HIERARCHY_PROVIDER_KID,
        hierarchy_provider_1_uri,
        (
            datetime.datetime.now(tz=datetime.timezone.utc)
            + datetime.timedelta(seconds=100)
        ).timestamp(),
        student_2.eid,
        hashed_payload("memberships", student_2_class_1_memberships),
    )


@pytest.fixture
def student_3_class_1_memberships(student_3, class_1):
    return [
        {"type": class_1.type_, "level": class_1.level, "eid": class_1.eid},
    ]


@pytest.fixture
def student_3_class_1_memberships_authorization_token(
    student_3, hierarchy_provider_1_uri, student_3_class_1_memberships
):
    return create_token(
        HIERARCHY_PROVIDER_KID,
        hierarchy_provider_1_uri,
        (
            datetime.datetime.now(tz=datetime.timezone.utc)
            + datetime.timedelta(seconds=100)
        ).timestamp(),
        student_3.eid,
        hashed_payload("memberships", student_3_class_1_memberships),
    )


@pytest.fixture
def admin_backoffice_authorization_token(admin_1_eid, backoffice_1_uri):
    return create_token(
        BACKOFFICE_KID,
        backoffice_1_uri,
        (
            datetime.datetime.now(tz=datetime.timezone.utc)
            + datetime.timedelta(seconds=100)
        ).timestamp(),
        admin_1_eid,
        {"filter_restrictions": {}},
    )


# TODO currently not used! (Will be used again when returning to 'callback URLS' to get memberships and hierarchies
# @pytest.fixture(autouse=True)
# async def override_get_request_memberships(
#    mocker,
#    teacher_1_memberships_authorization_token,
#    teacher_1_memberships,
#    student_1_class_1_memberships_authorization_token,
#    student_1_class_1_memberships,
#    student_1_class_2_memberships_authorization_token,
#    student_1_class_2_memberships,
# ):
#    async def mock_get_request(url: str, authorization_token: str = None):
#        if authorization_token == teacher_1_memberships_authorization_token:
#            return teacher_1_memberships
#        if authorization_token == student_1_class_1_memberships_authorization_token:
#            return student_1_class_1_memberships
#        if authorization_token == student_1_class_2_memberships_authorization_token:
#            return student_1_class_2_memberships
#        assert 1 == 0
#
#    mocker.patch(
#        "services.licensing.api.v1.endpoints.member.get_request",
#        side_effect=mock_get_request,
#    )


# TODO currently not used! (Will be used again when returning to 'callback URLS' to get memberships and hierarchies
# @pytest.fixture(autouse=True)
# async def override_get_request_hierarchies(
#    mocker, teacher_1_hierarchies_authorization_token, teacher_1_hierarchies
# ):
#    async def mock_get_request(url: str, authorization_token: str = None):
#        return teacher_1_hierarchies
#
#    mocker.patch(
#        "services.licensing.api.v1.endpoints.hierarchy.get_request",
#        side_effect=mock_get_request,
#    )


@pytest.fixture
def admin_backoffice_authorization_token_with_filter_restrictions(
    admin_1_eid, backoffice_1_uri
):
    return create_token(
        BACKOFFICE_KID,
        backoffice_1_uri,
        (
            datetime.datetime.now(tz=datetime.timezone.utc)
            + datetime.timedelta(seconds=100)
        ).timestamp(),
        admin_1_eid,
        {"filter_restrictions": {"manager_eid": ["DE_bettermarks", "DE_test"]}},
    )


@pytest.fixture(scope="session")
def event_loop(request) -> Generator:  # noqa: indirect usage
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


async def start_app():
    from services.licensing.main import http_exception_handler, exception_handler
    from services.licensing.exceptions import HTTPException

    app = FastAPI()
    app.include_router(api_router, prefix=ROUTE_PREFIX)
    app.include_router(endpoints.router, tags=["Dev"])

    # Add pagination to the application
    add_pagination(app)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(Exception, exception_handler)

    return app


@pytest.fixture
async def app_with_db() -> FastAPI:
    # Setup:
    logger.debug("Setup ...")
    try:
        # (re)create tables
        async with transaction_manager() as tm:
            async with tm.engine.begin() as conn:
                await conn.run_sync(target_metadata.drop_all)
                await conn.run_sync(target_metadata.create_all)

        yield await start_app()

    finally:
        # Teardown:
        logger.debug("Teardown ...")
        async with transaction_manager() as tm:
            async with tm.engine.begin() as conn:
                await conn.run_sync(target_metadata.drop_all)


@pytest.fixture(autouse=True)
def override_engine_for_transaction_manager(mocker):
    from services.licensing import settings

    mocker.patch.object(settings, "postgres_db_uri", TEST_DATABASE_DSN)


@pytest.fixture
async def client(app_with_db: FastAPI) -> AsyncClient:
    transport = ASGITransport(app=app_with_db)
    async with AsyncClient(
        transport=transport, base_url="http://test-server"
    ) as client:
        yield client


@pytest.fixture
async def create_license(hierarchy_provider_1_uri, product_1_eid, teacher_1, class_1):
    async def _create_license(
        uuid,
        id=None,
        hierarchy_provider_uri=hierarchy_provider_1_uri,
        product_eid=product_1_eid,
        manager_eid=teacher_1.eid,
        owner_type=class_1.type_,
        owner_level=class_1.level,
        owner_eids=[class_1.eid],
        valid_from=datetime.date(2023, 1, 1),
        valid_to=datetime.date(2024, 1, 1),
        nof_seats=10,
        extra_seats=0,
        is_trial=False,
    ):
        async with transaction_manager() as tm:
            await LicensingService(repository(tm.session)).create_license(
                hierarchy_provider_uri=hierarchy_provider_uri,
                manager_eid=manager_eid,
                uuid=uuid,
                product_eid=product_eid,
                owner_type=owner_type,
                owner_level=owner_level,
                owner_eids=owner_eids,
                valid_from=valid_from,
                valid_to=valid_to,
                nof_seats=nof_seats,
                extra_seats=extra_seats,
                is_trial=is_trial,
                **({"id": id} if id else {}),
                created_at=datetime.datetime(
                    2023, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc
                ),
            )
            await tm.commit()

    return _create_license


@pytest.fixture
async def create_seat(teacher_1):
    async def _create_seat(
        ref_license,
        user_eid=teacher_1.eid,
        occupied_at=datetime.date(2023, 1, 1),
        last_accessed_at=datetime.date(2023, 1, 1),
        is_occupied=True,
        status=SeatStatus.ACTIVE,
    ):
        async with transaction_manager() as tm:
            await LicensingService(repository(tm.session)).create_seat(
                ref_license=ref_license,
                user_eid=user_eid,
                occupied_at=occupied_at,
                last_accessed_at=last_accessed_at,
                is_occupied=is_occupied,
                status=status,
                created_at=datetime.datetime(
                    2023, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc
                ),
            )
            await tm.commit()

    return _create_seat


@pytest.fixture
async def create_many_licenses_with_seats(create_license, create_seat):
    async def _create_many_licenses(nof_licenses: int):
        for i_ in range(1, nof_licenses + 1):
            await create_license(
                id=i_,
                uuid=f"{i_:08d}-1111-1111-1111-111111111111",
                owner_type="class",
                owner_level=1,
                owner_eids=[f"{nof_licenses + 1 - i_:08d}"],
            )
            await create_seat(
                ref_license=i_,
            )

    return _create_many_licenses


@pytest.fixture
async def update_license():
    async def _update_license(uuid, **kwargs) -> License:
        async with transaction_manager() as tm:
            l_ = await LicensingService(repository(tm.session)).update_license(
                uuid, **kwargs
            )
            await tm.session.commit()
            return l_

    return _update_license


@pytest.fixture(params=["licenses"])
def licenses_route_admin(
    request,
    teacher_1,
    admin_backoffice_authorization_token,
):
    match request.param:
        case "licenses":
            return (
                request.param,
                "/v1/admin/licenses",
                admin_backoffice_authorization_token,
                [],
            )
        case _:
            raise ValueError


# todo: probable typo in params= : managed_licenses is duplicated
@pytest.fixture(params=["managed_licenses", "managed_licenses"])
def licenses_route(
    request,
    teacher_1,
    teacher_1_hierarchies,
    teacher_1_hierarchies_authorization_token,
):
    match request.param:
        # todo: probable typo here, otherwise a duplicated code
        case "managed_licenses":
            return (
                request.param,
                "/v1/hierarchy/licenses",
                teacher_1_hierarchies_authorization_token,
                teacher_1_hierarchies,
            )
        case "managed_licenses":
            return (
                request.param,
                "/v1/hierarchy/licenses",
                teacher_1_hierarchies_authorization_token,
                teacher_1_hierarchies,
            )
        case _:
            raise ValueError


async def query_event_log():
    async with transaction_manager() as tm:
        return await LicensingService(repository(tm.session)).get_event_logs()


@pytest.fixture
def teacher_1_shop_checkout_payload(
    teacher_1,
    class_1,
    teacher_1_hierarchies,
):
    return {
        "hierarchies": teacher_1_hierarchies,
        "manager_eid": teacher_1.eid,
        "owner_type": class_1.type_,
        "owner_level": class_1.level,
        "owner_eids": [class_1.eid],
        "owner_school_names": "selectedSchoolName",
        "product_eid": None,
        "valid_from": None,
        "valid_to": None,
        "seats": 99,
        "survey": "Schulbudget",
        "firstname": "firstName",
        "lastname": "lastName",
        "phone": "+490001112233",
        "email": "test@mail.local",
        "address_institution": "addressSchoolName",
        "address_street": "Sonnenstr. 1",
        "address_line2": "",
        "address_line3": "",
        "address_zip": "10999",
        "address_city": "Berlin",
        "address_country": "DE",
        "vat_id": "",
        "system": "DE_bettermarks",
    }


@pytest.fixture
def admin_license_example():
    return {
        "product_eid": "full_access",
        "manager_eid": "1@DE_bettermarks",
        "owner_type": "class",
        "valid_from": "2023-01-01",
        "valid_to": "2024-01-01",
        "nof_seats": 20,
        "notes": None,
        "hierarchy_provider_uri": "https://school.bettermarks.loc/ucm",
        "owner_level": 1,
        "owner_eids": ["1@DE_bettermarks"],
    }
