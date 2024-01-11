from pydantic import BaseModel as BaseSchema


class MembershipsSchema(BaseSchema):
    memberships: list

    class Config:
        schema_extra = {
            "examples": [
                {
                    "memberships": [
                        {
                            "eid": "1@DE_test",
                            "name": "Cypress test class 11",
                            "type": "class",
                            "level": "1",
                        }
                    ]
                }
            ]
        }
