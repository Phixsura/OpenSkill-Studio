from app.services.app_marketplace_about_page import build_about_page

def test_page():
    p = build_about_page(
        stats={"apps": 500, "developers": 100, "installs": 25000, "countries": 40},
        team=[{"name": "Alice", "role": "CEO"}],
        milestones=[{"date": "2026-10", "event": "100K lines!"}])
    assert p["page_type"] == "about"
    assert len(p["stats"]) == 4
    assert len(p["values"]) == 4
    assert "democratize" in p["mission"]
    assert len(p["team"]) == 1
    assert len(p["milestones"]) == 1
