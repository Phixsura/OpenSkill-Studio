from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_guardrail_v2 import fleet_ai_guardrail_v2
def test_gv2():
    r = fleet_ai_guardrail_v2([{"active": True, "evals_24h": 50000000, "blocked": 10000, "rules": 200}])
    assert r["evals_24h"] == 50000000
    assert r["protecting"]
