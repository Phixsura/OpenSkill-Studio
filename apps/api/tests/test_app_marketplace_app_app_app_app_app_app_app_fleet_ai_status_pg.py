from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_status_pg import fleet_ai_status_page
def test_sp():
    r = fleet_ai_status_page([{"status": "operational"}, {"status": "operational"}])
    assert r["overall"] == "operational"
    assert r["operational"] == 2
