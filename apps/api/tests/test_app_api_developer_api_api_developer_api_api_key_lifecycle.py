import pytest
from app.services.app_api_developer_api_api_developer_api_api_key_lifecycle import AppAPIDeveloperAPIApiDeveloperApiApiKeyLifecycle

class TestApiKeyLifecycle:
    def test_create(self):
        m = AppAPIDeveloperAPIApiDeveloperApiApiKeyLifecycle()
        r = m.create_key("inst-1", "k1", "Prod Key", "sk-prod-abcdefghijklmnop1234")
        assert r.prefix == "sk-prod-"
        assert r.status == "active"

    def test_short_key_rejected(self):
        m = AppAPIDeveloperAPIApiDeveloperApiApiKeyLifecycle()
        with pytest.raises(ValueError):
            m.create_key("inst-1", "k1", "Bad", "short")

    def test_use(self):
        m = AppAPIDeveloperAPIApiDeveloperApiApiKeyLifecycle()
        m.create_key("inst-1", "k1", "Key", "sk-test-abcdefghijklmnop12")
        r = m.use_key("inst-1", "k1")
        assert r.usage_count == 1

    def test_suspend_blocks_use(self):
        m = AppAPIDeveloperAPIApiDeveloperApiApiKeyLifecycle()
        m.create_key("inst-1", "k1", "Key", "sk-test-abcdefghijklmnop12")
        m.suspend("inst-1", "k1")
        with pytest.raises(ValueError, match="suspended"):
            m.use_key("inst-1", "k1")

    def test_revoke_cannot_reactivate(self):
        m = AppAPIDeveloperAPIApiDeveloperApiApiKeyLifecycle()
        m.create_key("inst-1", "k1", "Key", "sk-test-abcdefghijklmnop12")
        m.revoke("inst-1", "k1")
        with pytest.raises(ValueError, match="revoked"):
            m.reactivate("inst-1", "k1")

    def test_isolation(self):
        m = AppAPIDeveloperAPIApiDeveloperApiApiKeyLifecycle()
        m.create_key("inst-1", "k1", "Key", "sk-test-abcdefghijklmnop12")
        assert len(m.active_keys("inst-2")) == 0
