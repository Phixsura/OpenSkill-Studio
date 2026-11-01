from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_priv_vault import fleet_ai_privacy_vault
def test_pv():
    r = fleet_ai_privacy_vault([{"active": True, "pii_detected_24h": 50000, "redacted_24h": 50000, "tokenized": 30000}])
    assert r["secure"]
    assert r["tokenized"] == 30000
