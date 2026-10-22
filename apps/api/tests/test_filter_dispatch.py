"""More event dispatch filter tests covering all operators."""

from app.services.event_dispatch import EventDispatcher

d = EventDispatcher()

def test_eq_string(): assert d._matches_filter({"s": "abc"}, {"field": "s", "operator": "eq", "value": "abc"})
def test_eq_int(): assert d._matches_filter({"n": 42}, {"field": "n", "operator": "eq", "value": 42})
def test_eq_bool(): assert d._matches_filter({"b": True}, {"field": "b", "operator": "eq", "value": True})
def test_neq(): assert d._matches_filter({"x": 1}, {"field": "x", "operator": "neq", "value": 2})
def test_gte_exact(): assert d._matches_filter({"n": 70}, {"field": "n", "operator": "gte", "value": 70})
def test_gte_above(): assert d._matches_filter({"n": 71}, {"field": "n", "operator": "gte", "value": 70})
def test_gte_below(): assert not d._matches_filter({"n": 69}, {"field": "n", "operator": "gte", "value": 70})
def test_lte_exact(): assert d._matches_filter({"n": 70}, {"field": "n", "operator": "lte", "value": 70})
def test_lte_below(): assert d._matches_filter({"n": 69}, {"field": "n", "operator": "lte", "value": 70})
def test_lte_above(): assert not d._matches_filter({"n": 71}, {"field": "n", "operator": "lte", "value": 70})
def test_contains_yes(): assert d._matches_filter({"s": "hello world"}, {"field": "s", "operator": "contains", "value": "world"})
def test_contains_no(): assert not d._matches_filter({"s": "hello"}, {"field": "s", "operator": "contains", "value": "xyz"})
def test_in_yes(): assert d._matches_filter({"s": "a"}, {"field": "s", "operator": "in", "value": ["a", "b"]})
def test_in_no(): assert not d._matches_filter({"s": "c"}, {"field": "s", "operator": "in", "value": ["a", "b"]})
def test_nested_2(): assert d._matches_filter({"a": {"b": 1}}, {"field": "a.b", "operator": "eq", "value": 1})
def test_nested_3(): assert d._matches_filter({"a": {"b": {"c": "x"}}}, {"field": "a.b.c", "operator": "eq", "value": "x"})
def test_missing_field(): assert not d._matches_filter({}, {"field": "x", "operator": "eq", "value": 1})
def test_none_gte(): assert not d._matches_filter({"n": None}, {"field": "n", "operator": "gte", "value": 0})
def test_unknown_op(): assert d._matches_filter({"x": 1}, {"field": "x", "operator": "foo", "value": 1})
def test_empty_filter(): assert d._matches_filter({"x": 1}, {})
