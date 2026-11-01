"""Tests for App API Service Mesh — register, calls, links."""

from app.services.app_api_service_mesh import AppAPIServiceMesh


class TestRegister:
    def test_register(self):
        m = AppAPIServiceMesh()
        s = m.register_service("inst-1", "api", "API", "http://api:8080")
        assert s.error_rate == 0.0


class TestCalls:
    def test_record(self):
        m = AppAPIServiceMesh()
        m.register_service("inst-1", "api", "API", "http://api:8080")
        m.register_service("inst-1", "db", "Database", "http://db:5432")
        link = m.record_call("inst-1", "api", "db", True)
        assert link.call_count == 1

    def test_error_rate(self):
        m = AppAPIServiceMesh()
        m.register_service("inst-1", "db", "DB", "http://db:5432")
        for _ in range(9):
            m.record_call("inst-1", "api", "db", True)
        m.record_call("inst-1", "api", "db", False)
        db = [s for s in m.list_services("inst-1") if s.service_id == "db"][0]
        assert db.error_rate == 10.0


class TestLinks:
    def test_service_links(self):
        m = AppAPIServiceMesh()
        m.register_service("inst-1", "api", "API", "http://api")
        m.register_service("inst-1", "db", "DB", "http://db")
        m.register_service("inst-1", "cache", "Cache", "http://cache")
        m.record_call("inst-1", "api", "db", True)
        m.record_call("inst-1", "api", "cache", True)
        assert len(m.service_links("inst-1", "api")) == 2


class TestIsolation:
    def test_cross(self):
        m = AppAPIServiceMesh()
        m.register_service("inst-1", "api", "API", "http://api")
        assert m.list_services("inst-2") == []
