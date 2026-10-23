from app.services.app_marketplace_marketplace_footer import build_marketplace_footer

def test_footer():
    f = build_marketplace_footer(stats={"apps": 500, "developers": 100})
    assert len(f["sections"]) == 3
    assert "500 apps" in f["stats_bar"]
    assert f["copyright"] == "OpenSkill"
