from app.services.app_marketplace_app_app_app_app_app_app_app_deploy_cadence import analyze_cadence, cadence_health

def test_analyze():
    deploys = [{"date": f"2026-10-{i:02d}", "service": "api"} for i in range(1, 16)]
    r = analyze_cadence(deploys, period_days=15)
    assert r["total_deploys"] == 15
    assert r["deploys_per_day"] == 1.0
    assert r["services_deployed"] == 1

def test_cadence_elite():
    r = cadence_health(2.0)
    assert r["level"] == "elite"

def test_cadence_low():
    r = cadence_health(0.01)
    assert r["level"] == "low"
