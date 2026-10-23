from app.services.app_marketplace_app_app_app_app_app_app_app_status_badge import generate_badge, generate_status_badge, generate_uptime_badge

def test_badge():
    r = generate_badge(label="build", value="passing", color="green")
    assert "<svg" in r["svg"]
    assert "passing" in r["svg"]
    assert r["color"] == "#22C55E"
    assert r["content_type"] == "image/svg+xml"

def test_status():
    r = generate_status_badge(status="operational")
    assert "operational" in r["svg"]
    r2 = generate_status_badge(status="outage")
    assert r2["color"] == "#EF4444"

def test_uptime():
    r = generate_uptime_badge(99.95)
    assert "99.95%" in r["svg"]
    assert r["color"] == "#22C55E"
    r2 = generate_uptime_badge(98.5)
    assert r2["color"] == "#EF4444"
