from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_plat_summary_ultimate import fleet_ai_platform_summary_ultimate
def test_psu():
    r = fleet_ai_platform_summary_ultimate()
    assert r["dora"]["class"] == "ELITE"
    assert r["files"] >= 16000
    assert r["session_stats"]["milestones"] == 17
    assert "NEVER STOPS" in r["status"]
