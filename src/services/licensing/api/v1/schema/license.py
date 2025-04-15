import datetime
from typing import List, Optional
from typing_extensions import Annotated
import uuid as uuid_module
from pydantic import Field, StringConstraints

from services.licensing.api.v1.schema.base import BaseSchema

# Custom types
IntWithInfinity = Annotated[int, Field(strict=True, ge=-1)]
PositiveInt = Annotated[int, Field(strict=True, ge=0)]
NonEmptyStr = Annotated[str, StringConstraints(min_length=1, max_length=256)]


# Deserializer
class LicenseBaseDeserializerSchema(BaseSchema):
    owner_level: int
    owner_type: str = Field(min_length=1, max_length=256)
    nof_seats: Optional[IntWithInfinity] = Field(
        default=None,
        description=(
            "The absolute number of seats for a license that can be occupied. `-1` "
            "means unlimited."
        ),
    )
    extra_seats: Optional[PositiveInt] = Field(
        default=None,
        description=(
            "Extra seats make it possible to “overbook” the license seats of a license."
        ),
    )


class LicensePurchaseSchema(LicenseBaseDeserializerSchema):
    product_eid: str = Field(min_length=1, max_length=256)
    hierarchy_provider_uri: str = Field(min_length=1, max_length=256)
    owner_eids: List[NonEmptyStr]
    valid_from: datetime.date
    valid_to: datetime.date
    order_id: Optional[str] = Field(default=None, min_length=0, max_length=36)


class LicenseCreateSchema(LicensePurchaseSchema):
    """Admin license creation."""

    manager_eid: str = Field(min_length=1, max_length=256)
    notes: Optional[str] = Field(default=None, max_length=4096)


class LicenseUpdateSchema(BaseSchema):
    """Admin license update."""

    manager_eid: Optional[str] = Field(default=None, min_length=1, max_length=256)
    nof_seats: Optional[IntWithInfinity] = Field(
        default=None,
        description=(
            "The absolute number of seats for a license that can be occupied. `-1` "
            "means unlimited."
        ),
    )
    extra_seats: Optional[PositiveInt] = Field(
        default=None,
        description=(
            "Extra seats make it possible to “overbook” the license seats of a license."
        ),
    )
    valid_from: Optional[datetime.date] = None
    valid_to: Optional[datetime.date] = None


class LicenseTrialSchema(LicenseBaseDeserializerSchema):
    product_eid: str = Field(min_length=1, max_length=256)
    owner_eid: str
    memberships: list
    duration_weeks: Optional[int] = None

    class Config:
        json_schema_extra = {
            "example": {
                "owner_type": "class",
                "owner_level": 1,
                "owner_eid": "1@DE_bettermarks",
                "nof_seats": 50,
                "extra_seats": 0,
                "product_eid": "full_access",
            }
        }


# Serializer
class LicenseBaseSerializerSchema(BaseSchema):
    uuid: uuid_module.UUID
    product_eid: str
    owner_level: int
    owner_type: str = Field(min_length=1, max_length=256)
    nof_seats: IntWithInfinity = Field(
        description=(
            "The absolute number of seats for a license that can be occupied. `-1` "
            "means unlimited."
        ),
    )
    nof_free_seats: IntWithInfinity = Field(
        description=(
            "The absolute number of free seats for a license. `-1` means unlimited."
        ),
    )
    nof_occupied_seats: int
    extra_seats: PositiveInt = Field(
        default=0,
        description=(
            "Extra seats make it possible to “overbook” the license seats of a license."
        ),
    )
    is_trial: bool
    valid_from: datetime.date
    valid_to: datetime.date

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "uuid": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "product_eid": "string",
                "owner_level": 0,
                "owner_type": "string",
                "nof_seats": 0,
                "nof_free_seats": 0,
                "nof_occupied_seats": 0,
                "extra_seats": 0,
                "is_trial": True,
                "valid_from": "2024-02-13",
                "valid_to": "2024-02-13",
                "owner_eids": ["string"],
            }
        }


class LicenseCreatedSchema(LicenseBaseSerializerSchema):
    pass


class LicenseAvailableSchema(LicenseBaseSerializerSchema):
    owner_eids: List[str]


class LicenseManagedSchema(LicenseBaseSerializerSchema):
    owner_eids: List[str]
    created_at: datetime.datetime

    class Config:
        json_schema_extra = {
            "example": {
                "uuid": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "product_eid": "string",
                "owner_level": 0,
                "owner_type": "string",
                "nof_seats": 0,
                "nof_free_seats": 0,
                "nof_occupied_seats": 0,
                "extra_seats": 0,
                "is_trial": True,
                "valid_from": "2024-02-13",
                "valid_to": "2024-02-13",
                "owner_eids": ["string"],
                "created_at": "2024-02-13T11:44:32.521Z",
            }
        }


class LicenseValidSchema(LicenseBaseSerializerSchema):
    owner_eids: List[str]

    class Config:
        json_schema_extra = {
            "example": {
                "uuid": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "product_eid": "string",
                "owner_level": 0,
                "owner_type": "string",
                "nof_seats": 0,
                "nof_free_seats": 0,
                "nof_occupied_seats": 0,
                "extra_seats": 0,
                "is_trial": True,
                "valid_from": "2024-02-13",
                "valid_to": "2024-02-13",
                "owner_eids": ["string"],
            }
        }


class LicenseActiveSchema(LicenseValidSchema):
    pass


class LicenseCompleteSchema(LicenseBaseSerializerSchema):
    id: int
    manager_eid: str
    owner_eids: List[str]
    notes: Optional[str] = None
    created_at: datetime.datetime
    updated_at: Optional[datetime.datetime] = None
