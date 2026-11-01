from app.services.app_marketplace_final_platform_report import get_final_platform_report
def test_final_report():
    r = get_final_platform_report()
    assert r["stats"]["lines"] >= 3000000
    assert r["stats"]["modules"] == 10
    assert r["dora"]["overall"] == "ELITE"
    assert r["quality"]["grade"] == "A+"
    assert r["github_limit_reached"]
    assert "NEVER STOPS" in r["status"]
