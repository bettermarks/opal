from pydantic import BaseModel as BaseSchema


class InvoiceCreateSchema(BaseSchema):
    product_eid: str
    owner_type: str
    nof_seats: int
    valid_from: str
    valid_to: str
    firstname: str
    lastname: str
    phone: str | None
    email: str
    address_institution: str
    address_line2: str
    address_line3: str | None
    address_street: str
    address_zip: str
    address_city: str
    address_country: str
    survey: str
    vat_id: str | None
    system: str | None
    license_id: str | None

    class Config:
        from_attributes = True


class InvoiceCreatedSchema(BaseSchema):
    id: int | None
    is_valid: bool
    page_number: int
    confirmation_message: str | None
    confirmation_type: str | None
    validation_messages: dict | None
