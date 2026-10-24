from app.services.app_marketplace_app_app_app_app_app_app_app_deploy_cadence import track_cadence

def test_cadence():
    deploys = [{"day_of_week": "Mon", "environment": "production"}] * 30 + \
              [{"day_of_week": "Tue", "environment": "staging"}] * 15
    r = track_cadence(deploys, 30)
    assert r["total"] == 45
    assert r["per_day"] == 1.5
    assert r["dora_level"] == "elite"
    assert r["busiest_day"] == "Mon"
    assert r["by_environment"]["production"] == 30
