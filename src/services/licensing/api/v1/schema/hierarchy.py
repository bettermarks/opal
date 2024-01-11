from typing import List

from pydantic import BaseModel as BaseSchema, conlist


class HierarchiesSchema(BaseSchema):
    hierarchies: List[str] = conlist(str, min_items=1)

    class Config:
        schema_extra = {
            "examples": [
                {
                    "hierarchies": [
                        {
                            "eid": "NO_STATE@DE_test",
                            "name": "NO_STATE",
                            "type": "state",
                            "level": 10,
                            "is_member_of": "true",
                            "children": [],
                        }
                    ]
                }
            ]
        }
