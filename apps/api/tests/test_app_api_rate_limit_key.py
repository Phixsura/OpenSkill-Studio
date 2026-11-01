import pytest
from app.services.app_api_rate_limit_key import AppAPIRateLimitKey

class TestKey:
    def test_create(self):
        r = AppAPIRateLimitKey()
        k = r.create("inst-1", "k1", "ip", "10.0.0.1", 10, 60)
        assert k.remaining == 10

    def test_exhaust(self):
        r = AppAPIRateLimitKey()
        r.create("inst-1", "k1", "api_key", "key-abc", 2)
        r.increment("inst-1", "k1")
        r.increment("inst-1", "k1")
        assert r.is_allowed("inst-1", "k1") is False

    def test_invalid_strategy(self):
        r = AppAPIRateLimitKey()
        with pytest.raises(ValueError):
            r.create("inst-1", "k1", "magic", "x")

    def test_isolation(self):
        r = AppAPIRateLimitKey()
        r.create("inst-1", "k1", "ip", "x")
        assert r.list_keys("inst-2") == []
