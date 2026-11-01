from app.services.app_marketplace_final_ecosystem_check import run_final_ecosystem_check

def test_ecosystem():
    r = run_final_ecosystem_check()
    assert "FULLY OPERATIONAL" in r["status"]
    assert r["subsystem_count"] == 10
    assert r["total_services"] > 200
    assert r["total_components"] > 150
