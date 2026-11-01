from app.services.app_marketplace_app_app_app_app_app_app_app_tenant_meter import (
    record_usage, get_tenant_usage, top_tenants, clear_usage,
)

def test_record():
    clear_usage()
    record_usage("t1", "api_calls", 100)
    record_usage("t1", "api_calls", 50)
    record_usage("t1", "storage_mb", 25)
    r = get_tenant_usage("t1")
    assert r["resources"]["api_calls"] == 150
    assert r["resource_count"] == 2
    clear_usage()

def test_top():
    clear_usage()
    record_usage("t1", "api_calls", 500)
    record_usage("t2", "api_calls", 200)
    record_usage("t3", "api_calls", 800)
    top = top_tenants("api_calls", 2)
    assert top[0]["tenant_id"] == "t3"
    assert len(top) == 2
    clear_usage()
