import pytest
from app.services.app_api_developer_api_api_traffic_splitter import AppAPIDeveloperAPIApiTrafficSplitter

class TestTrafficSplitter:
    def test_create_rule(self):
        s = AppAPIDeveloperAPIApiTrafficSplitter()
        r = s.create_rule("inst-1", "r1", "/api/users", {"v1": 90, "v2": 10})
        assert r.splits["v1"] == 90

    def test_splits_must_total_100(self):
        s = AppAPIDeveloperAPIApiTrafficSplitter()
        with pytest.raises(ValueError, match="100"):
            s.create_rule("inst-1", "r1", "/api", {"v1": 50, "v2": 30})

    def test_route_deterministic(self):
        s = AppAPIDeveloperAPIApiTrafficSplitter()
        s.create_rule("inst-1", "r1", "/api", {"v1": 50, "v2": 50})
        v1 = s.route("inst-1", "r1", "req-1")
        v2 = s.route("inst-1", "r1", "req-1")
        assert v1 == v2  # same request_id = same version

    def test_distribution(self):
        s = AppAPIDeveloperAPIApiTrafficSplitter()
        s.create_rule("inst-1", "r1", "/api", {"v1": 50, "v2": 50})
        for i in range(100): s.route("inst-1", "r1", f"req-{i}")
        stats = s.stats("inst-1", "r1")
        assert stats["v1"] > 20  # roughly 50%
        assert stats["v2"] > 20

    def test_isolation(self):
        s = AppAPIDeveloperAPIApiTrafficSplitter()
        s.create_rule("inst-1", "r1", "/api", {"v1": 100})
        assert len(s.list_rules("inst-2")) == 0
