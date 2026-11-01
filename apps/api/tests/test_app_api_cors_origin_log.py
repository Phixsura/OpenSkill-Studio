"""Tests for App API CORS Origin Log — record, top, blocked."""

from app.services.app_api_cors_origin_log import AppAPICORSOriginLog


class TestRecord:
    def test_record(self):
        l = AppAPICORSOriginLog()
        r = l.record("inst-1", "https://app.com", True)
        assert r.request_count == 1
        assert r.allowed_count == 1

    def test_accumulate(self):
        l = AppAPICORSOriginLog()
        l.record("inst-1", "https://app.com", True)
        l.record("inst-1", "https://app.com", False)
        r = l.top_origins("inst-1")[0]
        assert r.request_count == 2
        assert r.block_rate == 50.0


class TestQuery:
    def test_top(self):
        l = AppAPICORSOriginLog()
        for _ in range(10):
            l.record("inst-1", "https://app.com", True)
        for _ in range(3):
            l.record("inst-1", "https://other.com", True)
        top = l.top_origins("inst-1")
        assert top[0].origin == "https://app.com"

    def test_blocked(self):
        l = AppAPICORSOriginLog()
        l.record("inst-1", "https://good.com", True)
        l.record("inst-1", "https://bad.com", False)
        assert len(l.blocked_origins("inst-1")) == 1


class TestIsolation:
    def test_cross(self):
        l = AppAPICORSOriginLog()
        l.record("inst-1", "https://app.com", True)
        assert l.unique_count("inst-2") == 0
