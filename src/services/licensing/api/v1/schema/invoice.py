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
    phone: Optional[str] = None
    email: str
    address_institution: str
    address_line2: str
    address_line3: Optional[str] = None
    address_street: str
    address_zip: str
    address_city: str
    address_country: str
    survey: str
    vat_id: Optional[str] = None
    system: Optional[str] = None
    license_id: Optional[str] = None

    class Config:
        from_attributes = True


class InvoiceCreatedSchema(BaseSchema):
    id: Optional[int] = None
    is_valid: bool
    page_number: int
    confirmation_message: Optional[str] = None
    confirmation_type: Optional[str] = None
    validation_messages: Optional[dict] = None
