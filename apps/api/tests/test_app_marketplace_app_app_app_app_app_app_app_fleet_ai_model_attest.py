from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_model_attest import fleet_ai_model_attestation
def test_ma():
    r = fleet_ai_model_attestation([{"active": True, "models": 500, "signatures": 500, "verifications": 10000}])
    assert r["signatures"] == 500
    assert r["trusted"]
