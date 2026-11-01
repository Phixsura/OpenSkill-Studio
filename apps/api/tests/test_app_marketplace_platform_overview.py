from app.services.app_marketplace_platform_overview import build_platform_overview

def test_overview():
    r = build_platform_overview()
    assert r["status"] == "operational"
    assert len(r["modules"]) == 10
    assert all(m["status"] == "operational" for m in r["modules"].values())
    assert r["stats"]["total_commits"] == 1350
    assert len(r["milestones"]) >= 4
