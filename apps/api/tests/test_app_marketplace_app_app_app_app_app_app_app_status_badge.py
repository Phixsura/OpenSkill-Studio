from app.services.app_marketplace_app_app_app_app_app_app_app_status_badge import generate_badge, generate_badges

def test_badge():
    r = generate_badge("build", "passing", "green")
    assert "<svg" in r["svg"]
    assert "passing" in r["svg"]
    assert "#4c1" in r["svg"]

def test_badges():
    r = generate_badges({"uptime_pct": 99.95, "version": "3.0.1", "status": "operational"})
    assert len(r) == 3
    assert any("uptime" in b["label"] for b in r)

def test_escape():
    r = generate_badge("<script>", "x&y")
    assert "<script>" not in r["svg"]
