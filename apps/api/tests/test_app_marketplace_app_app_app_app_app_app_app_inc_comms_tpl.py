from app.services.app_marketplace_app_app_app_app_app_app_app_inc_comms_tpl import generate_comms, comms_history

def test_generate():
    r = generate_comms("investigating", {"service": "API Gateway", "impact": "degraded performance"})
    assert r["generated"]
    assert "API Gateway" in r["message"]
    assert "investigating" in r["message"]

def test_resolved():
    r = generate_comms("resolved", {"service": "DB", "duration": "45 minutes", "cause": "connection pool"})
    assert r["generated"]
    assert "resolved" in r["message"]

def test_history():
    r = comms_history([{"type": "investigating"}, {"type": "resolved"}, {"type": "investigating"}])
    assert r["total"] == 3
    assert r["by_type"]["investigating"] == 2
