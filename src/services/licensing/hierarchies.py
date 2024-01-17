from functools import reduce
from typing import List, Dict

from services.licensing.custom_types import Entity


def parent_entities(
    hierarchies: List, parents: Dict[Entity, List[Entity]]
) -> Dict[Entity, List[Entity]]:
    """
    helper: builds up a dict with child entities as keys
    and lists of parent entities as values
    """
    for h_ in hierarchies:
        for c_ in h_.get("children", []):
            key = Entity(
                type_=c_["type"],
                eid=c_["eid"],
                level=c_.get("level", -1),
                name=c_.get("name", h_["eid"]),
                is_member_of=c_.get("is_member_of", False),
            )
            if not parents.get(key):
                parents[key] = []
            parents[key].append(
                Entity(
                    type_=h_["type"],
                    eid=h_["eid"],
                    level=h_.get("level", -1),
                    name=h_.get("name", h_["eid"]),
                    is_member_of=h_.get("is_member_of", False),
                )
            )
            parents = parent_entities([c_], parents)
    return parents


def get_ancestors(entity_type, entity_eid, hierarchies) -> List[Entity]:
    """
    helper: creates a list of all ancestors of a given entity in a given hierarchy
    """
    parents = hierarchies.get(Entity(type_=entity_type, eid=entity_eid)) or []
    return reduce(
        lambda acc, cur: acc + cur,
        [get_ancestors(p.type_, p.eid, hierarchies) for p in parents],
        parents,
    )
