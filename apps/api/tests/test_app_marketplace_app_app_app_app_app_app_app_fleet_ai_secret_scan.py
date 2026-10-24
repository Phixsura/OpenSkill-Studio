from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_secret_scan import fleet_ai_secret_scanner
def test_ss():
    r = fleet_ai_secret_scanner([{"active": True, "repos": 500, "secrets_found": 15, "revoked": 15}])
    assert r["repos"] == 500
    assert r["clean"]
