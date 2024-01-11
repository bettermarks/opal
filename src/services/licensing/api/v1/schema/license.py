import datetime
from typing import List
import uuid as uuid_module
from pydantic import BaseModel as BaseSchema, Field, constr, conint

from services.licensing.api.v1.schema.seat import SeatSchema

# Custom types
IntWithInfinity = conint(strict=True, ge=-1)
PositiveInt = conint(strict=True, ge=0)


# Deseriealizer
class LicenseBaseDeserializerSchema(BaseSchema):
    owner_level: int
    owner_type: str = Field(min_length=1, max_length=256)
    nof_seats: IntWithInfinity = Field(
        description=(
            "The absolute number of seats for a license that can be occupied. `-1` "
            "means unlimited."
        ),
    )
    extra_seats: PositiveInt = Field(
        default=0,
        description=(
            "Extra seats make it possible to “overbook” the license seats of a license."
        ),
    )


class LicensePurchaseSchema(LicenseBaseDeserializerSchema):
    product_eid: str = Field(min_length=1, max_length=256)
    hierarchy_provider_uri: str = Field(min_length=1, max_length=256)
    owner_eids: List[constr(min_length=1, max_length=256)]
    valid_from: datetime.date
    valid_to: datetime.date
    order_id: str | None = Field(min_length=0, max_length=36)


class LicenseCreateSchema(LicensePurchaseSchema):
    """Admin license creation."""

    manager_eid: str = Field(min_length=1, max_length=256)
    notes: str | None = Field(max_length=4096)


class LicenseUpdateSchema(BaseSchema):
    """Admin license update."""

    manager_eid: str | None = Field(min_length=1, max_length=256)
    nof_seats: IntWithInfinity | None = Field(
        description=(
            "The absolute number of seats for a license that can be occupied. `-1` "
            "means unlimited."
        ),
    )
    extra_seats: PositiveInt | None = Field(
        default=0,
        description=(
            "Extra seats make it possible to “overbook” the license seats of a license."
        ),
    )
    valid_from: datetime.date | None
    valid_to: datetime.date | None


class LicenseTrialSchema(LicenseBaseDeserializerSchema):
    product_eid: str = Field(min_length=1, max_length=256)
    owner_eid: str
    memberships: list
    duration_weeks: int | None

    class Config:
        json_schema_extra = {
            "example": {
                "owner_type": "class",
                "owner_level": 1,
                "owner_eid": "1@DE_test",
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


class LicenseCreatedSchema(LicenseBaseSerializerSchema):
    pass


class LicenseAvailableSchema(LicenseBaseSerializerSchema):
    owner_eids: List[str]
    seats: List[SeatSchema]


class LicenseManagedSchema(LicenseBaseSerializerSchema):
    owner_eids: List[str]
    seats: List[SeatSchema]
    released_seats: List[SeatSchema]
    created_at: datetime.datetime


class LicenseValidSchema(LicenseBaseSerializerSchema):
    owner_eids: List[str]


class LicenseActiveSchema(LicenseValidSchema):
    pass


class LicenseCompleteSchema(LicenseBaseSerializerSchema):
    id: int
    manager_eid: str
    owner_eids: List[str]
    notes: str | None
    seats: List[SeatSchema]
    released_seats: List[SeatSchema]
    created_at: datetime.datetime
    updated_at: datetime.datetime | None
