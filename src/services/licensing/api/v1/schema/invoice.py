from typing import Optional

from services.licensing.api.v1.schema.base import BaseSchema


class InvoiceCreateSchema(BaseSchema):
    product_eid: str
    owner_type: str
    nof_seats: int
    valid_from: str
    valid_to: str
    firstname: str
    lastname: str
    phone: str | None = None
    email: str
    address_institution: str
    address_line2: str
    address_line3: str | None = None
    address_street: str
    address_zip: str
    address_city: str
    address_country: str
    survey: str
    vat_id: str | None = None
    system: str | None = None
    license_id: str | None = None

    class Config:
        from_attributes = True


class InvoiceCreatedSchema(BaseSchema):
    id: int | None = None
    is_valid: bool
    page_number: int
    confirmation_message: str | None = None
    confirmation_type: str | None = None
    validation_messages: dict | None = None
