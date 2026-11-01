from app.services.app_marketplace_final_summary_v2 import get_platform_summary_v2

def test_summary():
    s = get_platform_summary_v2()
    assert s["status"] == "FULLY OPERATIONAL"
    assert len(s["modules"]) == 10
    assert all(m["status"] == "operational" for m in s["modules"].values())
    assert len(s["pages_built"]) >= 24
    assert s["all_tests_green"]
    assert s["stats"]["sdks"] if "sdks" in s["stats"] else True
