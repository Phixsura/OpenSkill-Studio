from app.services.app_marketplace_health_timeline import build_health_timeline, get_downtime_incidents, compute_mtbf

def test_timeline():
    checks = [{"timestamp": f"2026-01-01T{h:02d}:00:00Z", "status": "healthy", "response_ms": 100} for h in range(24)]
    t = build_health_timeline(checks=checks)
    assert t["uptime_pct"] == 100.0
    assert t["current_status"] == "healthy"

def test_downtime():
    timeline = [{"status": "healthy", "timestamp": "t1"}, {"status": "down", "timestamp": "t2"},
                {"status": "down", "timestamp": "t3"}, {"status": "healthy", "timestamp": "t4"}]
    incidents = get_downtime_incidents(timeline=timeline)
    assert len(incidents) == 1
    assert incidents[0]["resolved"]

def test_ongoing_incident():
    timeline = [{"status": "healthy", "timestamp": "t1"}, {"status": "down", "timestamp": "t2"}]
    incidents = get_downtime_incidents(timeline=timeline)
    assert not incidents[0]["resolved"]

def test_mtbf():
    r = compute_mtbf(incidents=[{"start": "t1"}, {"start": "t2"}], total_hours=720)
    assert r["mtbf_hours"] == 360.0
