"""Tests for App API Developer Activity — record, score, ranking."""

from app.services.app_api_developer_activity import AppAPIDeveloperActivity


class TestRecord:
    def test_record(self):
        a = AppAPIDeveloperActivity()
        act = a.record("inst-1", "dev-1", "/api/users", "2024-01-15")
        assert act.api_calls == 1
        assert len(act.active_days) == 1

    def test_accumulate(self):
        a = AppAPIDeveloperActivity()
        a.record("inst-1", "dev-1", "/api/users", "2024-01-15")
        act = a.record("inst-1", "dev-1", "/api/apps", "2024-01-16")
        assert act.api_calls == 2
        assert len(act.endpoints_used) == 2


class TestEngagement:
    def test_score(self):
        a = AppAPIDeveloperActivity()
        for i in range(10):
            a.record("inst-1", "dev-1", f"/api/ep{i}", f"2024-01-{15+i}")
        act = a.get_activity("inst-1", "dev-1")
        assert act is not None
        assert act.engagement_score > 0

    def test_top(self):
        a = AppAPIDeveloperActivity()
        for _ in range(10):
            a.record("inst-1", "dev-1", "/api", "2024-01-15")
        a.record("inst-1", "dev-2", "/api", "2024-01-15")
        top = a.top_developers("inst-1")
        assert top[0].developer_id == "dev-1"


class TestIsolation:
    def test_cross(self):
        a = AppAPIDeveloperActivity()
        a.record("inst-1", "dev-1", "/api", "2024-01-15")
        assert a.active_developer_count("inst-2") == 0
