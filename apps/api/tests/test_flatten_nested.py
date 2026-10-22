"""More flatten_dict edge cases."""

import pytest
from app.services.event_dispatch import EventDispatcher

d = EventDispatcher()

DEEP_CASES = [
    ({"a": {"b": {"c": {"d": "deep"}}}}, {"a.b.c.d": "deep"}),
    ({"x": 1, "y": {"z": 2}}, {"x": "1", "y.z": "2"}),
    ({"list": [1, 2]}, {"list": "[1, 2]"}),
    ({"bool": True}, {"bool": "True"}),
    ({"float": 3.14}, {"float": "3.14"}),
]

@pytest.mark.parametrize("input_dict,expected", DEEP_CASES)
def test_deep_flatten(input_dict, expected):
    result = d._flatten_dict(input_dict)
    assert result == expected
