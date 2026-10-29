import pytest
from app.services.app_api_developer_api_api_mock_server import AppAPIDeveloperAPIApiMockServer

class TestMockServer:
    def test_register(self):
        s = AppAPIDeveloperAPIApiMockServer()
        m = s.register("inst-1", "m1", "GET", "/api/users", 200, '{"data": []}')
        assert m.method == "GET"

    def test_match(self):
        s = AppAPIDeveloperAPIApiMockServer()
        s.register("inst-1", "m1", "GET", "/api/users")
        m = s.match("inst-1", "GET", "/api/users")
        assert m is not None
        assert m.hit_count == 1

    def test_no_match(self):
        s = AppAPIDeveloperAPIApiMockServer()
        s.register("inst-1", "m1", "GET", "/api/users")
        assert s.match("inst-1", "POST", "/api/users") is None

    def test_toggle(self):
        s = AppAPIDeveloperAPIApiMockServer()
        s.register("inst-1", "m1", "GET", "/api/users")
        s.toggle("inst-1", "m1", False)
        assert s.match("inst-1", "GET", "/api/users") is None

    def test_isolation(self):
        s = AppAPIDeveloperAPIApiMockServer()
        s.register("inst-1", "m1", "GET", "/api/users")
        assert len(s.list_mocks("inst-2")) == 0
