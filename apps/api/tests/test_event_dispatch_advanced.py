"""Advanced tests for event dispatch filter evaluation."""

from app.services.event_dispatch import EventDispatcher, PlatformEvent, CANONICAL_EVENTS


class TestFilterEvaluation:
    def setup_method(self):
        self.d = EventDispatcher()

    def test_eq_match(self):
        assert self.d._matches_filter({"status": "completed"}, {"field": "status", "operator": "eq", "value": "completed"})

    def test_eq_no_match(self):
        assert not self.d._matches_filter({"status": "failed"}, {"field": "status", "operator": "eq", "value": "completed"})

    def test_neq_match(self):
        assert self.d._matches_filter({"status": "failed"}, {"field": "status", "operator": "neq", "value": "completed"})

    def test_neq_no_match(self):
        assert not self.d._matches_filter({"status": "completed"}, {"field": "status", "operator": "neq", "value": "completed"})

    def test_gte_match(self):
        assert self.d._matches_filter({"score": 85}, {"field": "score", "operator": "gte", "value": 70})

    def test_gte_exact(self):
        assert self.d._matches_filter({"score": 70}, {"field": "score", "operator": "gte", "value": 70})

    def test_gte_no_match(self):
        assert not self.d._matches_filter({"score": 69}, {"field": "score", "operator": "gte", "value": 70})

    def test_lte_match(self):
        assert self.d._matches_filter({"score": 50}, {"field": "score", "operator": "lte", "value": 70})

    def test_lte_no_match(self):
        assert not self.d._matches_filter({"score": 71}, {"field": "score", "operator": "lte", "value": 70})

    def test_contains_match(self):
        assert self.d._matches_filter({"msg": "hello world"}, {"field": "msg", "operator": "contains", "value": "world"})

    def test_contains_no_match(self):
        assert not self.d._matches_filter({"msg": "hello"}, {"field": "msg", "operator": "contains", "value": "world"})

    def test_in_match(self):
        assert self.d._matches_filter({"status": "active"}, {"field": "status", "operator": "in", "value": ["active", "pending"]})

    def test_in_no_match(self):
        assert not self.d._matches_filter({"status": "archived"}, {"field": "status", "operator": "in", "value": ["active", "pending"]})

    def test_nested_field(self):
        assert self.d._matches_filter({"data": {"user": {"role": "admin"}}}, {"field": "data.user.role", "operator": "eq", "value": "admin"})

    def test_nested_field_missing(self):
        assert not self.d._matches_filter({"data": {}}, {"field": "data.user.role", "operator": "eq", "value": "admin"})

    def test_none_value_gte(self):
        assert not self.d._matches_filter({"score": None}, {"field": "score", "operator": "gte", "value": 70})

    def test_unknown_operator_passes(self):
        assert self.d._matches_filter({"x": 1}, {"field": "x", "operator": "unknown_op", "value": 1})

    def test_missing_field_passes_false(self):
        assert not self.d._matches_filter({}, {"field": "nonexistent", "operator": "eq", "value": "x"})

    def test_empty_filter(self):
        assert self.d._matches_filter({"x": 1}, {})


class TestPlatformEvent:
    def test_event_creation(self):
        e = PlatformEvent("test.event", {"key": "val"}, org_id="org-1")
        assert e.event_type == "test.event"
        assert e.org_id == "org-1"
        assert e.event_id
        assert e.timestamp

    def test_event_to_dict(self):
        e = PlatformEvent("test.event", {"x": 1})
        d = e.to_dict()
        assert d["event_type"] == "test.event"
        assert d["data"]["x"] == 1

    def test_deterministic_id(self):
        ts = "2026-01-01T00:00:00Z"
        e1 = PlatformEvent("t", {"a": 1}, timestamp=ts)
        e2 = PlatformEvent("t", {"a": 1}, timestamp=ts)
        assert e1.event_id == e2.event_id

    def test_different_data_different_id(self):
        ts = "2026-01-01T00:00:00Z"
        e1 = PlatformEvent("t", {"a": 1}, timestamp=ts)
        e2 = PlatformEvent("t", {"a": 2}, timestamp=ts)
        assert e1.event_id != e2.event_id


class TestCanonicalEvents:
    def test_count(self):
        assert len(CANONICAL_EVENTS) >= 35

    def test_all_have_dot(self):
        for event in CANONICAL_EVENTS:
            assert "." in event, f"Event '{event}' missing dot separator"

    def test_categories(self):
        cats = {e.split(".")[0] for e in CANONICAL_EVENTS}
        assert len(cats) >= 10
