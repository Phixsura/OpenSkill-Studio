import time
from app.services.app_api_developer_api_api_developer_api_api_developer_api_api_api_developer_api_error_pattern_detector import AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiDeveloperApiErrorPatternDetector

class TestErrorPatternDetector:
    def test_record(self):
        d = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiDeveloperApiErrorPatternDetector()
        p = d.record("inst-1", "RATE_LIMITED", "/api/users", "c1", time.time())
        assert p.occurrence_count == 1

    def test_accumulates(self):
        d = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiDeveloperApiErrorPatternDetector()
        for i in range(50): d.record("inst-1", "TIMEOUT", "/api", f"c{i % 5}", time.time())
        patterns = d.top_patterns("inst-1")
        assert patterns[0].occurrence_count == 50
        assert len(patterns[0].affected_consumers) == 5

    def test_severity(self):
        d = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiDeveloperApiErrorPatternDetector()
        for i in range(100): d.record("inst-1", "500", "/api", "c1", time.time())
        assert d.critical_patterns("inst-1")[0].severity == "critical"

    def test_by_endpoint(self):
        d = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiDeveloperApiErrorPatternDetector()
        d.record("inst-1", "404", "/a", "c1", time.time())
        d.record("inst-1", "500", "/b", "c1", time.time())
        assert len(d.by_endpoint("inst-1", "/a")) == 1

    def test_isolation(self):
        d = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiDeveloperApiErrorPatternDetector()
        d.record("inst-1", "500", "/api", "c1", time.time())
        assert len(d.top_patterns("inst-2")) == 0
