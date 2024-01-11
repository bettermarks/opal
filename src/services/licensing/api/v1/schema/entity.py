from pydantic import BaseModel as BaseSchema


class EntitySchema(BaseSchema):
    entity_type: str
    entity_eid: str
    hierarchies: list
