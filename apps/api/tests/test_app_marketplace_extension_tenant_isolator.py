from app.services.app_marketplace_extension_tenant_isolator import TenantIsolatorService
import pytest


def test_provision():
    ti = TenantIsolatorService()
    tenant = ti.provision("t1", "Acme Corp", "pro")
    assert tenant.plan == "pro"
    assert tenant.quotas["api_calls"] == 50000


def test_duplicate_provision():
    ti = TenantIsolatorService()
    ti.provision("t1", "Acme")
    with pytest.raises(ValueError):
        ti.provision("t1", "Duplicate")


def test_cross_tenant_blocked():
    ti = TenantIsolatorService()
    ti.provision("t1", "A")
    ti.provision("t2", "B")
    ti.store_data("t1", "users", {"name": "Alice"})
    with pytest.raises(PermissionError):
        ti.query_data("t1", "users", requesting_tenant="t2")


def test_same_tenant_access():
    ti = TenantIsolatorService()
    ti.provision("t1", "A")
    ti.store_data("t1", "users", {"name": "Alice"})
    data = ti.query_data("t1", "users", requesting_tenant="t1")
    assert len(data) == 1
    assert data[0]["name"] == "Alice"


def test_quota_enforcement():
    ti = TenantIsolatorService()
    ti.provision("t1", "Small", "free")
    # Free plan: 1000 API calls
    result = ti.check_quota("t1", "api_calls", 500)
    assert result["allowed"] is True
    result = ti.check_quota("t1", "api_calls", 600)
    assert result["allowed"] is False


def test_feature_flags():
    ti = TenantIsolatorService()
    ti.provision("t1", "Corp")
    ti.set_feature("t1", "beta_ui", True)
    assert ti.has_feature("t1", "beta_ui") is True
    assert ti.has_feature("t1", "other") is False


def test_noisy_neighbor():
    ti = TenantIsolatorService()
    t1 = ti.provision("t1", "Heavy")
    t2 = ti.provision("t2", "Light")
    t1.usage["api_calls"] = 9000
    t2.usage["api_calls"] = 1000
    noisy = ti.detect_noisy_neighbors("api_calls", threshold_pct=50)
    assert "t1" in noisy
    assert "t2" not in noisy


def test_upgrade_plan():
    ti = TenantIsolatorService()
    ti.provision("t1", "Starter", "free")
    ti.upgrade_plan("t1", "enterprise")
    stats = ti.get_tenant_stats("t1")
    assert stats["plan"] == "enterprise"
    assert stats["quotas"]["api_calls"] == 1000000


def test_deprovision():
    ti = TenantIsolatorService()
    ti.provision("t1", "Temp")
    ti.store_data("t1", "stuff", {"x": 1})
    ti.deprovision("t1")
    assert ti.get_tenant_stats("t1")["active"] is False


def test_data_isolation():
    ti = TenantIsolatorService()
    ti.provision("t1", "A")
    ti.provision("t2", "B")
    ti.store_data("t1", "items", {"id": 1})
    ti.store_data("t2", "items", {"id": 2})
    assert len(ti.query_data("t1", "items", "t1")) == 1
    assert ti.query_data("t1", "items", "t1")[0]["id"] == 1
