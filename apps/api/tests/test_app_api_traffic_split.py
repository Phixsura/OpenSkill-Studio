"""Tests for App API Traffic Split — create, route, distribution."""

import pytest
from app.services.app_api_traffic_split import AppAPITrafficSplit

TARGETS = [{"version": "v1", "weight": 90}, {"version": "v2", "weight": 10}]


class TestCreate:
    def test_create(self):
        t = AppAPITrafficSplit()
        s = t.create_split("inst-1", "s1", TARGETS)
        assert len(s.targets) == 2

    def test_bad_weights(self):
        t = AppAPITrafficSplit()
        with pytest.raises(ValueError, match="sum to 100"):
            t.create_split("inst-1", "s1", [{"version": "v1", "weight": 50}])


class TestRoute:
    def test_deterministic(self):
        t = AppAPITrafficSplit()
        t.create_split("inst-1", "s1", TARGETS)
        v1 = t.route("inst-1", "s1", "req-123")
        v2 = t.route("inst-1", "s1", "req-123")
        assert v1 == v2

    def test_distribution(self):
        t = AppAPITrafficSplit()
        t.create_split("inst-1", "s1", [{"version": "v1", "weight": 50}, {"version": "v2", "weight": 50}])
        versions = set()
        for i in range(100):
            versions.add(t.route("inst-1", "s1", f"req-{i}"))
        assert len(versions) == 2


class TestIsolation:
    def test_cross(self):
        t = AppAPITrafficSplit()
        t.create_split("inst-1", "s1", TARGETS)
        assert t.list_splits("inst-2") == []
