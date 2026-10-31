from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_final_status import fleet_final_status
def test_final():
    r = fleet_final_status()
    assert "OPERATIONAL" in r["status"]
    assert r["dora_grade"] == "Elite"
