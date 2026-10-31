"""EventDispatcher._flatten_dict tests."""

import pytest
from app.services.event_dispatch import EventDispatcher

d = EventDispatcher()

FLATTEN_CASES = [
    ({}, {}),
    ({"a": "1"}, {"a": "1"}),
    ({"a": {"b": "2"}}, {"a.b": "2"}),
    ({"a": {"b": {"c": "3"}}}, {"a.b.c": "3"}),
    ({"x": "1", "y": {"z": "2"}}, {"x": "1", "y.z": "2"}),
    ({"a": {"b": "1", "c": "2"}}, {"a.b": "1", "a.c": "2"}),
]

@pytest.mark.parametrize("input_dict,expected", FLATTEN_CASES)
def test_flatten(input_dict, expected):
    result = d._flatten_dict(input_dict)
    assert result == expected
