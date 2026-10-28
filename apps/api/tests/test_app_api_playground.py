"""Tests for App API Playground — templates, results, history."""

import pytest

from app.services.app_api_playground import AppAPIPlayground


class TestTemplate:
    def test_save(self):
        p = AppAPIPlayground()
        t = p.save_template("inst-1", "r1", "GET", "/api/v1/users", name="List Users")
        assert t.method == "GET"
        assert t.name == "List Users"

    def test_invalid_method(self):
        p = AppAPIPlayground()
        with pytest.raises(ValueError):
            p.save_template("inst-1", "r1", "BOGUS", "/api")


class TestResult:
    def test_record(self):
        p = AppAPIPlayground()
        r = p.record_result("inst-1", "r1", 200, '{"data": []}', 45.2)
        assert r.status_code == 200

    def test_history(self):
        p = AppAPIPlayground()
        for i in range(5):
            p.record_result("inst-1", f"r{i}", 200, "{}", 10.0)
        history = p.recent_history("inst-1", limit=3)
        assert len(history) == 3
        assert history[0].request_id == "r4"  # most recent first

    def test_retention(self):
        p = AppAPIPlayground(max_history=3)
        for i in range(5):
            p.record_result("inst-1", f"r{i}", 200, "{}", 10.0)
        assert len(p.recent_history("inst-1", limit=10)) == 3


class TestIsolation:
    def test_cross(self):
        p = AppAPIPlayground()
        p.save_template("inst-1", "r1", "GET", "/api")
        assert p.list_templates("inst-2") == []
