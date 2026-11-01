import time, pytest
from app.services.app_api_developer_api_deprecation_tracker import AppAPIDeveloperAPIDeprecationTracker

class TestDeprecationTracker:
    def test_deprecate(self):
        t = AppAPIDeveloperAPIDeprecationTracker()
        d = t.deprecate("inst-1", "/api/v1/old", time.time() + 86400 * 30, "/api/v2/new")
        assert d.replacement == "/api/v2/new"
        assert d.days_until_sunset > 29

    def test_record_hit(self):
        t = AppAPIDeveloperAPIDeprecationTracker()
        t.deprecate("inst-1", "/old", time.time() + 86400)
        t.record_hit("inst-1", "/old", "c1")
        t.record_hit("inst-1", "/old", "c1")
        t.record_hit("inst-1", "/old", "c2")
        d = t.most_used("inst-1")[0]
        assert d.hit_count == 3
        assert len(d.unique_consumers) == 2

    def test_past_sunset(self):
        t = AppAPIDeveloperAPIDeprecationTracker()
        t.deprecate("inst-1", "/old", time.time() - 1)
        assert len(t.past_sunset("inst-1")) == 1
        assert len(t.active("inst-1")) == 0

    def test_isolation(self):
        t = AppAPIDeveloperAPIDeprecationTracker()
        t.deprecate("inst-1", "/old", time.time() + 86400)
        assert len(t.active("inst-2")) == 0
