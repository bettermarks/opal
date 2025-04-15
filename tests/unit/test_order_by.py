import pytest

from services.licensing.custom_types import OrderByDirection
from services.licensing.order_by import get_order_by_fields
from services.licensing.exceptions import HTTPException


def test_order_by__ok():
    assert get_order_by_fields("-id.field1.-field2", ["id", "field1", "field2"]) == [
        ("id", OrderByDirection.DESC),
        ("field1", OrderByDirection.ASC),
        ("field2", OrderByDirection.DESC),
    ]


def test_order_by_empty__ok():
    assert get_order_by_fields("", ["id", "field1", "field2"]) == []


def test_order_by_none__ok():
    assert get_order_by_fields(None, ["id", "field1", "field2"]) == []


def test_order_by__not_allowed():
    with pytest.raises(HTTPException):
        get_order_by_fields("-id.field1.-field2.-field3", ["id", "field1", "field2"])


def test_order_by__illegal():
    with pytest.raises(HTTPException):
        get_order_by_fields("some:illegl-clause,given", ["id", "field1", "field2"])
