import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock
from uuid import UUID

from services.licensing.business.service import LicensingService
from services.licensing.custom_types import (
    Entity,
    Memberships,
    SeatStatus,
    License,
    Seat,
)


@pytest.fixture
def licensing_service():
    mock_repository = AsyncMock()
    service = LicensingService(licensing_repository=mock_repository)

    return service


@pytest.fixture
def memberships():
    return [
        Entity(
            eid="1@DE_bettermarks",
            type_="school",
            level=2,
            name="Cypress School 1",
            is_member_of=False,
        ),
        Entity(
            eid="2@DE_bettermarks",
            type_="class",
            level=1,
            name="Cypress test class for joining",
            is_member_of=False,
        ),
        Entity(
            eid="5@DE_bettermarks",
            type_="student",
            level=0,
            name="NA",
            is_member_of=False,
        ),
    ]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "occupied_seats, valid_licenses, expected_accessible_products",
    [
        # Case 1: No occupied seats, valid licenses available
        (
            [],
            [
                License(
                    id=6,
                    uuid=UUID("b54d5674-f5a7-4c85-9b4b-8a9dc8564a85"),
                    product_eid="full_access",
                    hierarchy_provider_uri="https://school.bettermarks.loc/ucm",
                    manager_eid="4@DE_bettermarks",
                    owner_type="class",
                    owner_level=1,
                    owner_eids=["83@DE_bettermarks"],
                    valid_from=datetime.now().date(),
                    valid_to=datetime.now().date() + timedelta(days=30),
                    nof_seats=10,
                    nof_free_seats=5,
                    nof_occupied_seats=5,
                    extra_seats=0,
                    is_trial=False,
                    notes=None,
                    seats=[],
                    released_seats=[],
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                )
            ],
            ["full_access"],
        ),
        # Case 2: Occupied seat exists, with expired license and disjointed membership
        (
            [
                Seat(
                    id=9,
                    user_eid="5@DE_bettermarks",
                    last_accessed_at=datetime.now(timezone.utc),
                    occupied_at=datetime.now(timezone.utc),
                    license=License(
                        id=5,
                        uuid=UUID("cf9b263a-3b97-4a76-9e6b-5481edce17ac"),
                        product_eid="full_access",
                        hierarchy_provider_uri="https://school.bettermarks.loc/ucm",
                        manager_eid="4@DE_bettermarks",
                        owner_type="class",
                        owner_level=1,
                        owner_eids=["24@DE_bettermarks"],  # disjointed membership
                        valid_from=datetime.now().date() - timedelta(days=60),
                        valid_to=datetime.now().date()
                        - timedelta(days=1),  # Expired license
                        nof_seats=15,
                        nof_free_seats=0,
                        nof_occupied_seats=15,
                        extra_seats=0,
                        is_trial=False,
                        notes=None,
                        seats=[],
                        released_seats=[],
                        created_at=datetime.now(),
                        updated_at=datetime.now(),
                    ),
                    status=SeatStatus.ACTIVE,  # with expired license, still start as active...
                    is_occupied=True,  # ...and occupied
                )
            ],
            [],
            [],
        ),
        # Case 3: User has two accessible products
        (
            [
                Seat(
                    id=10,
                    user_eid="5@DE_bettermarks",
                    last_accessed_at=datetime.now(timezone.utc),
                    occupied_at=datetime.now(timezone.utc),
                    license=License(
                        id=5,
                        uuid=UUID("cf9b263a-3b97-4a76-9e6b-5481edce17ac"),
                        product_eid="full_access",
                        hierarchy_provider_uri="https://school.bettermarks.loc/ucm",
                        manager_eid="9@DE_bettermarks",
                        owner_type="class",
                        owner_level=1,
                        owner_eids=["2@DE_bettermarks"],
                        valid_from=datetime.now().date(),
                        valid_to=datetime.now().date() + timedelta(days=30),
                        nof_seats=15,
                        nof_free_seats=0,
                        nof_occupied_seats=15,
                        extra_seats=0,
                        is_trial=False,
                        notes=None,
                        seats=[],
                        released_seats=[],
                        created_at=datetime.now(),
                        updated_at=datetime.now(),
                    ),
                    status=SeatStatus.ACTIVE,
                    is_occupied=True,
                )
            ],
            [
                License(
                    id=7,
                    uuid=UUID("b54d5674-f5a7-4c85-9b4b-8a9dc8564a85"),
                    product_eid="physics_access",
                    hierarchy_provider_uri="https://school.bettermarks.loc/ucm",
                    manager_eid="4@DE_bettermarks",
                    owner_type="school",
                    owner_level=1,
                    owner_eids=["1@DE_bettermarks"],
                    valid_from=datetime.now().date(),
                    valid_to=datetime.now().date() + timedelta(days=30),
                    nof_seats=10,
                    nof_free_seats=10,
                    nof_occupied_seats=0,
                    extra_seats=0,
                    is_trial=False,
                    notes=None,
                    seats=[],
                    released_seats=[],
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                )
            ],
            ["full_access", "physics_access"],
        ),
    ],
)
async def test_get_accessible_products(
    licensing_service,
    memberships,
    occupied_seats,
    valid_licenses,
    expected_accessible_products,
):
    licensing_service.licensing_repository.get_occupied_seats = AsyncMock(
        return_value=occupied_seats
    )
    licensing_service.licensing_repository.get_valid_licenses_for_entities = AsyncMock(
        return_value=valid_licenses
    )
    licensing_service.licensing_repository.update_seats = AsyncMock()
    licensing_service.licensing_repository.create_event_log = AsyncMock()

    result = await licensing_service.get_accessible_products(
        hierarchy_provider_uri="https://school.bettermarks.loc/ucm",
        user_eid="5@DE_bettermarks",
        memberships=memberships,
    )

    assert result == expected_accessible_products
    licensing_service.licensing_repository.update_seats.assert_called_once()
    # PermissionsRequestedEvent
    if not expected_accessible_products:
        licensing_service.licensing_repository.create_event_log.assert_called_once()
    # SeatCreatedEvent and PermissionsRequestedEvent
    else:
        assert licensing_service.licensing_repository.create_event_log.call_count == 2
