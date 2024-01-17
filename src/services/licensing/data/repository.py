"""
Here the 'repository pattern' in order to connect our business logic to our data
layer in a flexible and exchangeable way. The repository pattern (explained by
ChatGPT) is as follows:

The repository pattern is a way to separate the application's business logic from
the data storage and retrieval operations. It helps to keep the code organized and
maintainable by defining a clear separation of concerns between the application's
business logic and the data access layer.

In this pattern, the data access layer is abstracted away from the rest of the
application, and is represented by a repository interface. This interface defines
a set of methods that the rest of the application can use to interact with the
database, without needing to know any details about how the data is actually stored.

The repository interface is then implemented by a concrete repository class that
provides the actual implementation of the data storage and retrieval operations.
This class is responsible for performing the CRUD (Create, Read, Update, Delete)
operations on the database, while the rest of the application can interact with
it using the methods defined in the repository interface.

By using the repository pattern, the application's business logic is decoupled
from the data access layer, making it easier to maintain and test. It also allows
for easier swapping out of the data storage layer, since the rest of the
application is only dependent on the repository interface, and not on the actual
implementation of the data storage and retrieval operations.
"""

import datetime
from typing import List, Any, Tuple, Dict
from abc import ABC, abstractmethod

from services.licensing.custom_types import (
    License,
    Seat,
    EventLog,
    EventType,
    Entity,
)


class LicensingRepository(ABC):
    @abstractmethod
    def __init__(self, session: Any):
        pass

    @abstractmethod
    async def create_license(self, **license_data) -> None:
        pass

    @abstractmethod
    async def create_seat(self, **seat_data) -> None:
        pass

    @abstractmethod
    async def update_license(
        self, license_uuid: str, license_filter_restrictions: Any, **data
    ) -> License:
        pass

    @abstractmethod
    async def update_seats(self, seats: List[Seat]) -> None:
        pass

    @abstractmethod
    async def get_licenses_for_entities_paginated(
        self,
        page: int,
        page_size: int,
        order_by_fields: List[Tuple[str, str]],
        hierarchy_provider_uri: str,
        entities: List[Entity],
    ) -> List[License]:
        pass

    @abstractmethod
    async def get_managed_licenses_paginated(
        self,
        page: int,
        page_size: int,
        order_by_fields: List[Tuple[str, str]],
        hierarchy_provider_uri: str,
        user_eid: str,
    ) -> List[License]:
        pass

    @abstractmethod
    async def get_licenses_paginated(
        self,
        page: int,
        page_size: int,
        order_by_fields: List[Tuple[str, str]],
        filter_restrictions: Dict[str, List[str]],
        allowed_filter_restrictions: List[str],
        **filters
    ) -> List[License]:
        pass

    async def get_license(
        self,
        license_uuid: str,
        filter_restrictions: Dict[str, List[str]],
        allowed_filter_restrictions: List[str],
    ) -> License:
        pass

    @abstractmethod
    async def get_valid_licenses_for_entities(
        self,
        hierarchy_provider_uri: str,
        entities: List[Entity],
        when: datetime.date,
    ) -> List[License]:
        pass

    @abstractmethod
    async def get_occupied_seats(self, user_eid: str) -> List[Seat]:
        pass

    async def create_event_log(
        self,
        type_: EventType,
        payload: Dict[str, Any],
        version: int = 1,
        is_exported: bool = False,
    ):
        pass

    async def get_event_log_stats(self) -> Tuple[int, int]:
        pass

    async def get_event_logs(
        self, is_exported=False, order_by_latest=False, limit=1000000
    ) -> List[EventLog]:
        pass

    async def update_event_log(self, event_log_id: int, **data) -> None:
        pass
