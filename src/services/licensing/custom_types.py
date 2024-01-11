import datetime
import enum
import uuid as uuid_module
from dataclasses import dataclass
from typing import Dict, List, Any


class SeatStatus(enum.Enum):
    """
    A custom Enum type representing our 'seat status'
    """

    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    NOT_A_MEMBER = "NOT_A_MEMBER"

    def __str__(self):
        return self.value


class OrderByDirection(enum.Enum):
    """
    A custom Enum type representing abstract 'order by' directions
    """

    ASC = "ASC"
    DESC = "DESC"


@dataclass
class Entity:
    """
    Class representing an 'entity'. An entity can be a user, a class,
    a school, even  a country
    """

    eid: str
    type_: str
    level: int | None = None
    name: str | None = None
    is_member_of: bool = False

    def __hash__(self):
        return hash((self.type_, self.eid))

    def __eq__(self, other):
        if not isinstance(other, Entity):
            return False
        return self.type_ == other.type_ and self.eid == other.eid


@dataclass
class License:
    """
    DTO for licenses
    """

    id: int
    uuid: uuid_module.UUID
    product_eid: str
    hierarchy_provider_uri: str
    manager_eid: str
    owner_type: str
    owner_level: int
    owner_eids: List[str]
    valid_from: datetime.date
    valid_to: datetime.date
    nof_seats: int
    nof_free_seats: int
    extra_seats: int
    is_trial: bool
    notes: str
    seats: List[Any] | None
    released_seats: List[Any] | None
    created_at: datetime.datetime
    updated_at: datetime.datetime


@dataclass
class Seat:
    """
    DTO for seats
    """

    id: int
    user_eid: str
    last_accessed_at: datetime.datetime
    occupied_at: datetime.datetime
    license: License | None
    status: SeatStatus
    is_occupied: bool


class EventType(enum.Enum):
    """
    types of events
    """

    LICENSE_CREATED = "LicenseCreatedEvent"
    LICENSE_UPDATED = "LicenseUpdatedEvent"
    PERMISSIONS_REQUESTED = "PermissionsRequestedEvent"
    SEAT_CREATED = "SeatCreatedEvent"
    SEAT_UPDATED = "SeatUpdatedEvent"

    def __str__(self):
        return self.value


@dataclass
class EventLog:
    """
    DTO for eventlog
    """

    event_id: int | None
    event_type: EventType
    event_version: int
    event_timestamp: datetime
    event_payload: Dict[str, Any]


Memberships = List[Entity]
Hierarchies = Dict[Entity, List[Entity]]
