from app.services.app_marketplace_final_platform_v2 import run_final_platform_check_v2

def test_platform():
    r = run_final_platform_check_v2()
    assert "FULLY OPERATIONAL" in r["status"]
    assert r["module_count"] == 10
    assert r["total_features"] > 30
    assert all(m["all_operational"] for m in r["modules"].values())
