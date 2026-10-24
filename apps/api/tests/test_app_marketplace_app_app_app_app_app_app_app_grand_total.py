from app.services.app_marketplace_app_app_app_app_app_app_app_grand_total import platform_grand_total

def test_grand_total():
    r = platform_grand_total()
    assert r["status"] == "FULLY OPERATIONAL"
    assert r["stats"]["modules"] == 10
    assert r["all_tests_green"]
    assert len(r["modules"]) == 10
    assert r["stats"]["security_fixes"] == 3
