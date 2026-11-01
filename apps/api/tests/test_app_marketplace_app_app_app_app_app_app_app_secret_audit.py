from app.services.app_marketplace_app_app_app_app_app_app_app_secret_audit import audit_secrets

def test_audit():
    now = 100 * 86400  # day 100
    secrets = [
        {"name": "DB_PASSWORD", "created_at": 5 * 86400},   # 95 days old → overdue
        {"name": "API_KEY", "created_at": 50 * 86400},      # 50 days → ok
        {"name": "JWT_SECRET", "created_at": 88 * 86400},   # 12 days → warning
    ]
    r = audit_secrets(secrets, max_age_days=90, now=now)
    assert r["total"] == 3
    assert r["compliant"] == 2
    assert r["non_compliant"] == 1
    assert r["compliance_pct"] == 67
    db = next(s for s in r["results"] if s["name"] == "DB_PASSWORD")
    assert db["status"] == "overdue"
    jwt = next(s for s in r["results"] if s["name"] == "JWT_SECRET")
    assert jwt["status"] == "ok"  # 12 days old, 78 days until rotation
