from app.services.app_marketplace_app_app_status_badge import generate_badge, build_badge_set

def test_badge():
    r = generate_badge(label="build", value="passing", status="passing")
    assert "shields.io" in r["svg_url"]
    assert "brightgreen" in r["svg_url"]
    assert "![build]" in r["markdown"]

def test_badge_set():
    badges = [
        {"label": "build", "value": "passing", "status": "passing"},
        {"label": "coverage", "value": "95%", "status": "active"},
    ]
    r = build_badge_set(badges=badges)
    assert r["total"] == 2
    assert "![build]" in r["combined_markdown"]
    assert "![coverage]" in r["combined_markdown"]
