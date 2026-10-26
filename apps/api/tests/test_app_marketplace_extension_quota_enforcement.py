from app.services.app_marketplace_extension_quota_enforcement import (
    QuotaEnforcementService, ResourceType, QuotaState,
)
import pytest


def test_set_and_consume():
    svc = QuotaEnforcementService()
    svc.set_quota("ext-1", ResourceType.API_CALLS, 800, 1000)
    r = svc.consume("ext-1", ResourceType.API_CALLS, 500)
    assert r["allowed"] is True
    assert r["remaining"] == 500


def test_soft_limit_warning():
    svc = QuotaEnforcementService()
    svc.set_quota("ext-1", ResourceType.STORAGE_MB, 80, 100)
    svc.consume("ext-1", ResourceType.STORAGE_MB, 85)
    r = svc.check("ext-1", ResourceType.STORAGE_MB)
    assert r["state"] == "warning"


def test_hard_limit_blocked():
    svc = QuotaEnforcementService()
    svc.set_quota("ext-1", ResourceType.BANDWIDTH_MB, 80, 100)
    svc.consume("ext-1", ResourceType.BANDWIDTH_MB, 90)
    r = svc.consume("ext-1", ResourceType.BANDWIDTH_MB, 20)
    assert r["allowed"] is False
    assert "Hard limit" in r["reason"]


def test_release():
    svc = QuotaEnforcementService()
    svc.set_quota("ext-1", ResourceType.CONCURRENT_CONNECTIONS, 8, 10)
    svc.consume("ext-1", ResourceType.CONCURRENT_CONNECTIONS, 5)
    svc.release("ext-1", ResourceType.CONCURRENT_CONNECTIONS, 3)
    r = svc.check("ext-1", ResourceType.CONCURRENT_CONNECTIONS)
    assert r["current"] == 2


def test_usage_percent():
    svc = QuotaEnforcementService()
    svc.set_quota("ext-1", ResourceType.COMPUTE_SECONDS, 300, 500)
    svc.consume("ext-1", ResourceType.COMPUTE_SECONDS, 250)
    r = svc.check("ext-1", ResourceType.COMPUTE_SECONDS)
    assert r["usage_percent"] == 50.0


def test_invalid_limits():
    svc = QuotaEnforcementService()
    with pytest.raises(ValueError, match="Soft limit"):
        svc.set_quota("ext-1", ResourceType.API_CALLS, 100, 50)


def test_reset():
    svc = QuotaEnforcementService()
    svc.set_quota("ext-1", ResourceType.API_CALLS, 80, 100)
    svc.consume("ext-1", ResourceType.API_CALLS, 50)
    assert svc.reset("ext-1", ResourceType.API_CALLS) is True
    r = svc.check("ext-1", ResourceType.API_CALLS)
    assert r["current"] == 0


def test_get_all():
    svc = QuotaEnforcementService()
    svc.set_quota("ext-1", ResourceType.API_CALLS, 800, 1000)
    svc.set_quota("ext-1", ResourceType.STORAGE_MB, 80, 100)
    all_q = svc.get_all_quotas("ext-1")
    assert len(all_q) == 2
