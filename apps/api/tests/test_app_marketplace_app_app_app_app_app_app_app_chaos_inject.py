from app.services.app_marketplace_app_app_app_app_app_app_app_chaos_inject import ChaosInjector

def test_latency_injection():
    ci = ChaosInjector(seed=1)
    r = ci.inject_latency("api", 100, 500, pct=100)
    assert r["type"] == "latency"
    assert r["added_ms"] >= 100

def test_error_injection():
    ci = ChaosInjector(seed=1)
    r = ci.inject_error("api", 503, pct=100)
    assert r["triggered"]

def test_partition():
    ci = ChaosInjector()
    r = ci.inject_partition("web", "api")
    assert r["active"]
    s = ci.summary()
    assert s["total_experiments"] == 1
    assert s["by_type"]["network_partition"] == 1
