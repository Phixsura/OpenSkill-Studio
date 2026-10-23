from app.services.app_marketplace_app_developer_app_status_page_v2 import build_status_page_v2, generate_status_embed

def test_operational():
    p = build_status_page_v2(services=[{"name": "API", "status": "operational"}],
                              incidents=[], maintenance=[], uptime_90d=99.99)
    assert p["overall_status"] == "operational"
    assert len(p["subscribe_options"]) == 4

def test_outage():
    p = build_status_page_v2(services=[{"name": "API", "status": "major_outage"}],
                              incidents=[{"status": "investigating"}], maintenance=[], uptime_90d=98.5)
    assert p["overall_status"] == "major_outage"
    assert len(p["active_incidents"]) == 1

def test_embed():
    e = generate_status_embed(status="operational", uptime=99.99)
    assert e["badge_color"] == "#22c55e"
    assert "99.99%" in e["uptime_text"]
