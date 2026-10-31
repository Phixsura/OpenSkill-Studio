from app.services.app_marketplace_app_app_status_indicator import get_status_indicator, get_aggregate_status

def test_indicator():
    r = get_status_indicator(status="operational")
    assert r["icon"] == "🟢"
    assert r["label"] == "Operational"

def test_degraded():
    r = get_status_indicator(status="major_outage")
    assert r["icon"] == "🔴"

def test_aggregate_all_ok():
    comps = [{"status": "operational"}, {"status": "operational"}]
    r = get_aggregate_status(components=comps)
    assert r["all_operational"]
    assert r["status"] == "operational"

def test_aggregate_worst():
    comps = [{"status": "operational"}, {"status": "degraded"}, {"status": "major_outage"}]
    r = get_aggregate_status(components=comps)
    assert r["status"] == "major_outage"
    assert r["healthy_count"] == 1
