from app.services.app_marketplace_app_app_app_app_resource_usage import build_resource_usage

def test_ok():
    r = build_resource_usage(cpu_pct=45, memory_mb=256, memory_limit_mb=512,
                              bandwidth_mb=500, bandwidth_limit_mb=1000,
                              storage_mb=200, storage_limit_mb=1000)
    assert r["overall"] == "ok"
    assert r["resources"][0]["status"] == "ok"

def test_critical():
    r = build_resource_usage(cpu_pct=95, memory_mb=480, memory_limit_mb=512,
                              bandwidth_mb=950, bandwidth_limit_mb=1000,
                              storage_mb=100, storage_limit_mb=1000)
    assert r["overall"] == "critical"
