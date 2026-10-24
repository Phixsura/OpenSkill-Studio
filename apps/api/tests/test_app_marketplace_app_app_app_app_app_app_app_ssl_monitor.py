from app.services.app_marketplace_app_app_app_app_app_app_app_ssl_monitor import check_certificates, renewal_plan

def test_check():
    r = check_certificates([
        {"domain": "api.example.com", "issuer": "letsencrypt", "days_until_expiry": 90},
        {"domain": "web.example.com", "issuer": "letsencrypt", "days_until_expiry": 15},
        {"domain": "old.example.com", "issuer": "letsencrypt", "days_until_expiry": -5},
    ])
    assert r["valid"] == 1
    assert r["expiring_soon"] == 1
    assert r["expired"] == 1
    assert r["critical"]

def test_plan():
    plan = renewal_plan([
        {"domain": "a.com", "days_until_expiry": 20},
        {"domain": "b.com", "days_until_expiry": 3},
    ])
    assert plan[0]["domain"] == "b.com"
    assert plan[0]["action"] == "renew_immediately"
    assert plan[1]["action"] == "schedule_renewal"
