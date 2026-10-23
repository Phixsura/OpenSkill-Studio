from app.services.app_marketplace_app_app_app_app_app_app_app_tenant_isolation import (
    validate_tenant_access, partition_data, tenant_stats,
)

def test_access():
    assert validate_tenant_access("t1", "t1")["allowed"]
    assert validate_tenant_access("t1", "t2")["violation"]

def test_partition():
    records = [{"tenant_id": "t1", "data": "a"}, {"tenant_id": "t1", "data": "b"},
               {"tenant_id": "t2", "data": "c"}]
    r = partition_data(records, "t1")
    assert r["own_count"] == 2
    assert r["leaked_count"] == 1

def test_stats():
    tenants = {"t1": {"status": "active", "user_count": 50, "storage_mb": 100},
               "t2": {"status": "suspended", "user_count": 10, "storage_mb": 20}}
    r = tenant_stats(tenants)
    assert r["active"] == 1
    assert r["total_users"] == 60
