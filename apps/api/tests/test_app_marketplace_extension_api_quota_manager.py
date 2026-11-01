from app.services.app_marketplace_extension_api_quota_manager import (
    ApiQuotaManagerService, QuotaTier,
)


def test_register_and_check():
    svc = ApiQuotaManagerService()
    svc.register("ext-1", QuotaTier.FREE)
    r = svc.check_and_consume("ext-1")
    assert r.allowed is True
    assert r.remaining_hourly == 99


def test_hourly_limit():
    svc = ApiQuotaManagerService()
    svc.register("ext-1", QuotaTier.FREE)
    # Consume all hourly (100)
    for _ in range(100):
        svc.check_and_consume("ext-1")
    # Next should use burst
    r = svc.check_and_consume("ext-1")
    assert r.allowed is True
    assert r.used_burst is True


def test_burst_exhausted():
    svc = ApiQuotaManagerService()
    svc.register("ext-1", QuotaTier.FREE)
    # Exhaust hourly (100) + burst (20)
    for _ in range(120):
        svc.check_and_consume("ext-1")
    r = svc.check_and_consume("ext-1")
    assert r.allowed is False
    assert "limit exceeded" in r.reason.lower()


def test_override_limits():
    svc = ApiQuotaManagerService()
    svc.register("ext-1", QuotaTier.FREE)
    svc.set_override("ext-1", requests_per_hour=5)
    for _ in range(5):
        svc.check_and_consume("ext-1")
    r = svc.check_and_consume("ext-1")
    assert r.used_burst is True  # exceeded overridden hourly


def test_reset_hourly():
    svc = ApiQuotaManagerService()
    svc.register("ext-1", QuotaTier.FREE)
    svc.check_and_consume("ext-1", count=50)
    svc.reset_hourly("ext-1")
    usage = svc.get_usage("ext-1")
    assert usage["hourly"]["used"] == 0
    assert usage["daily"]["used"] == 50  # daily not reset


def test_get_usage():
    svc = ApiQuotaManagerService()
    svc.register("ext-1", QuotaTier.PRO)
    svc.check_and_consume("ext-1", count=10)
    u = svc.get_usage("ext-1")
    assert u["tier"] == "pro"
    assert u["hourly"]["used"] == 10
    assert u["hourly"]["limit"] == 10000


def test_unregistered():
    svc = ApiQuotaManagerService()
    r = svc.check_and_consume("unknown")
    assert r.allowed is False
    assert "not registered" in r.reason.lower()
