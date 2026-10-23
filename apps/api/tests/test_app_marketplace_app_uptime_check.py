from app.services.app_marketplace_app_uptime_check import run_uptime_checks, get_uptime_percentage

def test_checks():
    r = run_uptime_checks(endpoint="https://api.example.com/health")
    assert r["regions_checked"] == 4
    assert r["status"] == "operational"
    assert r["avg_latency_ms"] > 0

def test_custom_regions():
    r = run_uptime_checks(endpoint="https://x.com", regions=["us-east", "eu-west"])
    assert r["regions_checked"] == 2

def test_uptime():
    r = get_uptime_percentage(total_checks=10000, failed_checks=5)
    assert r["uptime_pct"] == 99.95
    assert r["nines"] == "99.9%"

def test_uptime_zero():
    r = get_uptime_percentage(total_checks=0, failed_checks=0)
    assert r["uptime_pct"] == 100.0
