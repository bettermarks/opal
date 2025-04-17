from services.licensing.api.v1.schema.base import BaseSchema


class EntitySchema(BaseSchema):
    entity_type: str
    entity_eid: str
    hierarchies: list
