from app.services.app_marketplace_app_app_resource_limiter import build_resource_config, list_presets

def test_preset():
    r = build_resource_config(preset="medium")
    assert r["cpu_m"] == 500
    assert r["memory_mb"] == 512
    assert r["replicas"] == 2
    assert r["monthly_cost_usd"] > 0

def test_custom():
    r = build_resource_config(cpu_m=750, memory_mb=768, replicas=2)
    assert r["cpu_m"] == 750
    assert r["replicas"] == 2

def test_display():
    r = build_resource_config(preset="xlarge")
    assert "2.0 cores" in r["cpu_display"]
    assert "2.0GB" in r["memory_display"]

def test_list():
    p = list_presets()
    assert len(p) == 5
    assert p[0]["id"] == "micro"
