import pytest

from services.licensing.custom_types import Entity
from services.licensing.hierarchies import parent_entities, get_ancestors


@pytest.fixture
def hierarchies_payload():
    return [
        {
            "eid": "cc1",
            "type": "cc",
            "name": "cc1",
            "level": 3,
            "children": [
                {
                    "eid": "cc1_s1",
                    "type": "s",
                    "name": "cc1_s1",
                    "level": 2,
                    "children": [
                        {
                            "eid": "cc1_s1_k1",
                            "type": "c",
                            "name": "cc1_s1_k1",
                            "level": 1,
                        },
                        {
                            "eid": "cc1_s1_k2",
                            "type": "c",
                            "name": "cc1_s1_k2",
                            "level": 1,
                        },
                    ],
                },
                {
                    "eid": "cc1_s2",
                    "type": "s",
                    "name": "cc1_s2",
                    "level": 2,
                    "children": [
                        {
                            "eid": "cc1_s2_k1",
                            "type": "c",
                            "name": "cc1_s2_k1",
                            "level": 1,
                        },
                        {
                            "eid": "cc1_s2_k2",
                            "type": "c",
                            "name": "cc1_s2_k2",
                            "level": 1,
                        },
                    ],
                },
            ],
        }
    ]


def test_parent_entities__ok(hierarchies_payload):
    hierarchies = parent_entities(hierarchies_payload, {})
    assert hierarchies == {
        Entity(
            eid="cc1_s1_k1", type_="c", level=1, name="cc1_s1_k1", is_member_of=False
        ): [
            Entity(eid="cc1_s1", type_="s", level=2, name="cc1_s1", is_member_of=False)
        ],
        Entity(
            eid="cc1_s1_k2", type_="c", level=1, name="cc1_s1_k2", is_member_of=False
        ): [Entity(eid="cc1_s1", type_="s", level=2, name="cc1", is_member_of=False)],
        Entity(
            eid="cc1_s2_k1", type_="c", level=1, name="cc1_s2_k1", is_member_of=False
        ): [
            Entity(eid="cc1_s2", type_="s", level=2, name="cc1_s2", is_member_of=False)
        ],
        Entity(
            eid="cc1_s2_k2", type_="c", level=1, name="cc1_s2_k2", is_member_of=False
        ): [
            Entity(eid="cc1_s2", type_="s", level=2, name="cc1_s2", is_member_of=False)
        ],
        Entity(eid="cc1_s1", type_="s", level=2, name="cc1_s1", is_member_of=False): [
            Entity(eid="cc1", type_="cc", level=3, name="cc1", is_member_of=False)
        ],
        Entity(eid="cc1_s2", type_="s", level=2, name="cc1_s2", is_member_of=False): [
            Entity(eid="cc1", type_="cc", level=3, name="cc1", is_member_of=False)
        ],
    }


def test_ancestors_for_level3__ok(hierarchies_payload):
    hierarchies = parent_entities(hierarchies_payload, {})
    ancestors = get_ancestors("cc", "cc1", hierarchies)
    assert ancestors == []


def test_ancestors_for_level2_1__ok(hierarchies_payload):
    hierarchies = parent_entities(hierarchies_payload, {})
    ancestors = get_ancestors("s", "cc1_s1", hierarchies)
    assert ancestors == [
        Entity(eid="cc1", type_="cc", level=3, name="cc1", is_member_of=False)
    ]


def test_ancestors_for_level2_2__ok(hierarchies_payload):
    hierarchies = parent_entities(hierarchies_payload, {})
    ancestors = get_ancestors("s", "cc1_s2", hierarchies)
    assert ancestors == [
        Entity(eid="cc1", type_="cc", level=3, name="cc1", is_member_of=False)
    ]


def test_ancestors_for_level1_11__ok(hierarchies_payload):
    hierarchies = parent_entities(hierarchies_payload, {})
    ancestors = get_ancestors("c", "cc1_s1_k1", hierarchies)
    assert ancestors == [
        Entity(eid="cc1_s1", type_="s", level=2, name="cc1_s1", is_member_of=False),
        Entity(eid="cc1", type_="cc", level=3, name="cc1", is_member_of=False),
    ]


def test_ancestors_for_level1_12__ok(hierarchies_payload):
    hierarchies = parent_entities(hierarchies_payload, {})
    ancestors = get_ancestors("c", "cc1_s1_k2", hierarchies)
    assert ancestors == [
        Entity(eid="cc1_s1", type_="s", level=2, name="cc1_s1", is_member_of=False),
        Entity(eid="cc1", type_="cc", level=3, name="cc1", is_member_of=False),
    ]


def test_ancestors_for_level1_21__ok(hierarchies_payload):
    hierarchies = parent_entities(hierarchies_payload, {})
    ancestors = get_ancestors("c", "cc1_s2_k1", hierarchies)
    assert ancestors == [
        Entity(eid="cc1_s2", type_="s", level=2, name="cc1_s2", is_member_of=False),
        Entity(eid="cc1", type_="cc", level=3, name="cc1", is_member_of=False),
    ]


def test_ancestors_for_level1_22__ok(hierarchies_payload):
    hierarchies = parent_entities(hierarchies_payload, {})
    ancestors = get_ancestors("c", "cc1_s2_k2", hierarchies)
    assert ancestors == [
        Entity(eid="cc1_s2", type_="s", level=2, name="cc1_s2", is_member_of=False),
        Entity(eid="cc1", type_="cc", level=3, name="cc1", is_member_of=False),
    ]
