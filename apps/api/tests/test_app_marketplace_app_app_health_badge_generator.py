from app.services.app_marketplace_app_app_health_badge_generator import generate_health_badge

def test_healthy():
    r = generate_health_badge(app_name="Auth SDK", status="healthy", uptime_pct=99.99)
    assert "22c55e" in r["badge_url"]
    assert "![Auth SDK" in r["markdown"]
    assert r["status"] == "healthy"

def test_down():
    r = generate_health_badge(app_name="API", status="down", uptime_pct=85.0)
    assert "ef4444" in r["color"]

def test_xss():
    r = generate_health_badge(app_name="<script>", status="ok", uptime_pct=100)
    assert "<script>" not in r["markdown"]
