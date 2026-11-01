from app.services.app_marketplace_app_app_app_app_app_app_app_token_meter import (
    record_usage, get_usage, usage_summary, clear_usage,
)

def test_record():
    clear_usage()
    record_usage("tk1", "/api/users", 5)
    record_usage("tk1", "/api/data", 3)
    r = get_usage("tk1")
    assert r["found"]
    assert r["total"] == 8
    assert r["top_endpoint"] == "/api/users"
    assert r["endpoint_count"] == 2
    clear_usage()

def test_summary():
    clear_usage()
    record_usage("a", "/x", 100)
    record_usage("b", "/y", 200)
    s = usage_summary()
    assert s["total_consumed"] == 300
    assert s["active_keys"] == 2
    assert s["avg_per_key"] == 150
    clear_usage()
