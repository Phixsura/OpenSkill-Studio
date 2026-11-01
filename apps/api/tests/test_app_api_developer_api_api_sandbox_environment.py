import pytest
from app.services.app_api_developer_api_api_sandbox_environment import AppAPIDeveloperAPIApiSandboxEnvironment

class TestSandboxEnvironment:
    def test_create(self):
        e = AppAPIDeveloperAPIApiSandboxEnvironment()
        s = e.create("inst-1", "s1", "Test Sandbox", "https://sandbox.api.com")
        assert s.status == "active"

    def test_https_required(self):
        e = AppAPIDeveloperAPIApiSandboxEnvironment()
        with pytest.raises(ValueError):
            e.create("inst-1", "s1", "Bad", "http://insecure.com")

    def test_use(self):
        e = AppAPIDeveloperAPIApiSandboxEnvironment()
        e.create("inst-1", "s1", "Test", "https://sandbox.com")
        e.use("inst-1", "s1")
        s = e.all_sandboxes("inst-1")[0]
        assert s.request_count == 1

    def test_expired(self):
        e = AppAPIDeveloperAPIApiSandboxEnvironment()
        s = e.create("inst-1", "s1", "Test", "https://sandbox.com", ttl_hours=0)
        import time; s.expires_at = time.time() - 1
        with pytest.raises(ValueError, match="expired"):
            e.use("inst-1", "s1")

    def test_isolation(self):
        e = AppAPIDeveloperAPIApiSandboxEnvironment()
        e.create("inst-1", "s1", "Test", "https://sandbox.com")
        assert len(e.all_sandboxes("inst-2")) == 0
