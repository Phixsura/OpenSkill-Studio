import pytest
from app.services.app_api_developer_api_api_developer_api_api_developer_api_playground import AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiPlayground

class TestApiPlayground:
    def test_execute(self):
        p = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiPlayground()
        r = p.execute("inst-1", "r1", "GET", "/api/users", 200, '{"data": []}', 45)
        assert r.method == "GET"

    def test_invalid_method(self):
        p = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiPlayground()
        with pytest.raises(ValueError):
            p.execute("inst-1", "r1", "HACK", "/api", 200)

    def test_save(self):
        p = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiPlayground()
        p.execute("inst-1", "r1", "GET", "/api", 200)
        r = p.save("inst-1", "r1")
        assert r.saved is True
        assert len(p.saved_requests("inst-1")) == 1

    def test_history(self):
        p = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiPlayground()
        p.execute("inst-1", "r1", "GET", "/a", 200)
        p.execute("inst-1", "r2", "POST", "/b", 201)
        h = p.history("inst-1")
        assert h[0].request_id == "r2"

    def test_stats(self):
        p = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiPlayground()
        p.execute("inst-1", "r1", "GET", "/a", 200)
        p.execute("inst-1", "r2", "GET", "/b", 500)
        s = p.stats("inst-1")
        assert s["total"] == 2
        assert s["errors"] == 1

    def test_isolation(self):
        p = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiPlayground()
        p.execute("inst-1", "r1", "GET", "/a", 200)
        assert p.stats("inst-2")["total"] == 0
