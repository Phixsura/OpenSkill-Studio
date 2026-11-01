from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_dpo import fleet_ai_dpo
def test_dpo():
    r = fleet_ai_dpo([{"active": True, "pairs": 500000, "epochs": 3, "win_rate": 72}])
    assert r["pairs"] == 500000
    assert r["aligned"]
