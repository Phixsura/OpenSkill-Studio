from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_dev_exp import fleet_ai_developer_experience
def test_de():
    r = fleet_ai_developer_experience([{"active": True, "nps": 72, "ttfc_min": 5, "docs_pct": 95}])
    assert r["nps"] == 72
    assert r["excellent"]
