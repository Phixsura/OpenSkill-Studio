"""Parametrized flatten_dict tests."""

import pytest
from app.services.event_dispatch import EventDispatcher

d = EventDispatcher()

CASES = [
    ({}, {}),
    ({"a": "1"}, {"a": "1"}),
    ({"a": {"b": "2"}}, {"a.b": "2"}),
    ({"a": {"b": {"c": "3"}}}, {"a.b.c": "3"}),
    ({"x": 1, "y": 2}, {"x": "1", "y": "2"}),
    ({"a": None}, {"a": ""}),
    ({"a": {"b": 1}, "c": "d"}, {"a.b": "1", "c": "d"}),
]

@pytest.mark.parametrize("input_dict,expected", CASES)
def test_flatten(input_dict, expected):
    result = d._flatten_dict(input_dict)
    assert result == expected
