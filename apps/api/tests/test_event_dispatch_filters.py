"""EventDispatcher filter operator tests."""

import pytest
from app.services.event_dispatch import EventDispatcher

d = EventDispatcher()

FILTER_CASES = [
    # (data, filter_expr, expected)
    ({"status": "active"}, {"field": "status", "operator": "eq", "value": "active"}, True),
    ({"status": "active"}, {"field": "status", "operator": "eq", "value": "inactive"}, False),
    ({"status": "active"}, {"field": "status", "operator": "neq", "value": "inactive"}, True),
    ({"status": "active"}, {"field": "status", "operator": "neq", "value": "active"}, False),
    ({"count": 10}, {"field": "count", "operator": "gte", "value": 10}, True),
    ({"count": 10}, {"field": "count", "operator": "gte", "value": 11}, False),
    ({"count": 10}, {"field": "count", "operator": "lte", "value": 10}, True),
    ({"count": 10}, {"field": "count", "operator": "lte", "value": 9}, False),
    ({"name": "hello world"}, {"field": "name", "operator": "contains", "value": "world"}, True),
    ({"name": "hello"}, {"field": "name", "operator": "contains", "value": "xyz"}, False),
    ({"role": "admin"}, {"field": "role", "operator": "in", "value": ["admin", "mod"]}, True),
    ({"role": "user"}, {"field": "role", "operator": "in", "value": ["admin", "mod"]}, False),
    # nested path
    ({"user": {"role": "admin"}}, {"field": "user.role", "operator": "eq", "value": "admin"}, True),
    ({"user": {"role": "admin"}}, {"field": "user.role", "operator": "eq", "value": "user"}, False),
    # missing field — defaults to pass
    ({}, {"field": "missing", "operator": "eq", "value": "x"}, False),
]

@pytest.mark.parametrize("data,filter_expr,expected", FILTER_CASES,
    ids=lambda x: str(x)[:40])
def test_filter_operator(data, filter_expr, expected):
    assert d._matches_filter(data, filter_expr) is expected
