from typing import List, Dict, Any

from pydantic import conlist

from services.licensing.api.v1.schema.base import BaseSchema


class HierarchiesSchema(BaseSchema):
    hierarchies: List[Dict[str, Any]] = conlist(Dict, min_length=1)

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "hierarchies": [
                        {
                            "eid": "NO_STATE@DE_bettermarks",
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
