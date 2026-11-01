from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_dx_v7 import fleet_ai_dx_v7
def test_dxv7():
    r = fleet_ai_dx_v7([{"active": True, "nps": 80, "ttfc_min": 3, "docs_pct": 98, "sdk_pct": 85}])
    assert r["nps"] == 80
    assert r["excellent"]
