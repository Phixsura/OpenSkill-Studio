import pytest
from app.services.app_api_developer_api_api_playground_runner import AppAPIDeveloperAPIApiPlaygroundRunner

class TestPlaygroundRunner:
    def test_execute(self):
        r = AppAPIDeveloperAPIApiPlaygroundRunner()
        e = r.execute("inst-1", "e1", "GET", "/api/users", 200, '{"data": []}', 45.0)
        assert e.method == "GET"
        assert e.status_code == 200

    def test_invalid_method(self):
        r = AppAPIDeveloperAPIApiPlaygroundRunner()
        with pytest.raises(ValueError):
            r.execute("inst-1", "e1", "INVALID", "/api", 200, "", 0)

    def test_history(self):
        r = AppAPIDeveloperAPIApiPlaygroundRunner()
        r.execute("inst-1", "e1", "GET", "/a", 200, "", 10)
        r.execute("inst-1", "e2", "POST", "/b", 201, "", 20)
        h = r.history("inst-1")
        assert h[0].execution_id == "e2"  # most recent first

    def test_by_status(self):
        r = AppAPIDeveloperAPIApiPlaygroundRunner()
        r.execute("inst-1", "e1", "GET", "/a", 200, "", 10)
        r.execute("inst-1", "e2", "GET", "/b", 500, "", 50)
        assert len(r.by_status("inst-1", 400)) == 1

    def test_isolation(self):
        r = AppAPIDeveloperAPIApiPlaygroundRunner()
        r.execute("inst-1", "e1", "GET", "/a", 200, "", 10)
        assert len(r.history("inst-2")) == 0
