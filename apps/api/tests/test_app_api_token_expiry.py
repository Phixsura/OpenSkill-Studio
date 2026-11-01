import time
from app.services.app_api_token_expiry import AppAPITokenExpiry

class TestExpiry:
    def test_register(self):
        e = AppAPITokenExpiry()
        t = e.register("inst-1", "t1", "Prod Key", time.time() + 86400)
        assert t.days_remaining >= 0

    def test_expired(self):
        e = AppAPITokenExpiry()
        e.register("inst-1", "t1", "Old Key", time.time() - 100)
        assert len(e.expired("inst-1")) == 1

    def test_expiring_soon(self):
        e = AppAPITokenExpiry()
        e.register("inst-1", "t1", "Soon", time.time() + 86400 * 7)
        e.register("inst-1", "t2", "Later", time.time() + 86400 * 60)
        assert len(e.expiring_soon("inst-1", within_days=30)) == 1

    def test_isolation(self):
        e = AppAPITokenExpiry()
        e.register("inst-1", "t1", "A", time.time() + 100)
        assert e.list_tokens("inst-2") == []
