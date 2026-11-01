"""Tests for App Playground Runner — execute, save, history."""

import pytest

from app.services.app_playground_runner import (
    AppPlaygroundRunner,
    PlaygroundRequest,
    PlaygroundResponse,
)


def _req(rid="r1", method="GET", path="/api/users"):
    return PlaygroundRequest(request_id=rid, method=method, path=path)


def _resp(status=200, body='{"data":[]}', duration=45.0):
    return PlaygroundResponse(status_code=status, body=body, duration_ms=duration)


class TestExecute:
    def test_execute(self):
        r = AppPlaygroundRunner()
        e = r.execute("inst-1", "e1", _req(), _resp(), now=1000.0)
        assert e.execution_id == "e1"
        assert e.request.method == "GET"
        assert e.response.status_code == 200

    def test_duplicate(self):
        r = AppPlaygroundRunner()
        r.execute("inst-1", "e1", _req(), _resp())
        with pytest.raises(ValueError, match="already exists"):
            r.execute("inst-1", "e1", _req(), _resp())

    def test_with_name(self):
        r = AppPlaygroundRunner()
        e = r.execute("inst-1", "e1", _req(), _resp(), name="List users")
        assert e.name == "List users"


class TestSave:
    def test_save(self):
        r = AppPlaygroundRunner()
        r.execute("inst-1", "e1", _req(), _resp())
        e = r.save_execution("inst-1", "e1", name="Saved request")
        assert e.saved is True
        assert e.name == "Saved request"

    def test_not_found(self):
        r = AppPlaygroundRunner()
        with pytest.raises(KeyError):
            r.save_execution("inst-1", "nope")


class TestHistory:
    def test_newest_first(self):
        r = AppPlaygroundRunner()
        r.execute("inst-1", "e1", _req("r1"), _resp(), now=1000.0)
        r.execute("inst-1", "e2", _req("r2"), _resp(), now=1001.0)
        h = r.get_history("inst-1")
        assert h[0].execution_id == "e2"

    def test_limit(self):
        r = AppPlaygroundRunner()
        for i in range(10):
            r.execute("inst-1", f"e{i}", _req(f"r{i}"), _resp())
        h = r.get_history("inst-1", limit=3)
        assert len(h) == 3

    def test_saved_only(self):
        r = AppPlaygroundRunner()
        r.execute("inst-1", "e1", _req("r1"), _resp())
        r.execute("inst-1", "e2", _req("r2"), _resp())
        r.save_execution("inst-1", "e1")
        h = r.get_history("inst-1", saved_only=True)
        assert len(h) == 1

    def test_max_history_trims(self):
        r = AppPlaygroundRunner(max_history=5)
        for i in range(8):
            r.execute("inst-1", f"e{i}", _req(f"r{i}"), _resp())
        h = r.get_history("inst-1", limit=100)
        assert len(h) == 5


class TestIsolation:
    def test_cross_installation(self):
        r = AppPlaygroundRunner()
        r.execute("inst-1", "e1", _req(), _resp())
        with pytest.raises(KeyError):
            r.get_execution("inst-2", "e1")
