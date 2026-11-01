import pytest
from app.services.app_api_developer_api_api_idempotency_key_store import AppAPIDeveloperAPIApiIdempotencyKeyStore

class TestIdempotencyKeyStore:
    def test_first_request(self):
        s = AppAPIDeveloperAPIApiIdempotencyKeyStore()
        is_dup, r = s.get_or_create("inst-1", "k1", '{"ok": true}', 200)
        assert is_dup is False

    def test_duplicate(self):
        s = AppAPIDeveloperAPIApiIdempotencyKeyStore()
        s.get_or_create("inst-1", "k1", '{"ok": true}', 200)
        is_dup, r = s.get_or_create("inst-1", "k1", '{"ok": true}', 200)
        assert is_dup is True
        assert r.hit_count == 1

    def test_key_too_long(self):
        s = AppAPIDeveloperAPIApiIdempotencyKeyStore()
        with pytest.raises(ValueError, match="too long"):
            s.get_or_create("inst-1", "x" * 300, "{}", 200)

    def test_expired_treated_as_new(self):
        s = AppAPIDeveloperAPIApiIdempotencyKeyStore(default_ttl=0)
        s.get_or_create("inst-1", "k1", "{}", 200)
        import time; time.sleep(0.01)
        is_dup, _ = s.get_or_create("inst-1", "k1", "{}", 200)
        assert is_dup is False

    def test_stats(self):
        s = AppAPIDeveloperAPIApiIdempotencyKeyStore()
        s.get_or_create("inst-1", "k1", "{}", 200)
        s.get_or_create("inst-1", "k1", "{}", 200)
        st = s.stats("inst-1")
        assert st["active_keys"] == 1
        assert st["total_hits"] == 1

    def test_isolation(self):
        s = AppAPIDeveloperAPIApiIdempotencyKeyStore()
        s.get_or_create("inst-1", "k1", "{}", 200)
        assert not s.exists("inst-2", "k1")
