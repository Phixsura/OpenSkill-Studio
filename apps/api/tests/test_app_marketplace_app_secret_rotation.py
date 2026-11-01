from app.services.app_marketplace_app_secret_rotation import rotate_secret, get_rotation_schedule

def test_rotate():
    r = rotate_secret(secret_id="sk1", rotation_type="api_key")
    assert len(r["new_value"]) > 20
    assert r["old_hash"] != r["new_hash"]
    assert "24h" in r["warning"]

def test_schedule():
    secrets_list = [
        {"id": "s1", "name": "API Key", "age_days": 95, "max_age_days": 90},
        {"id": "s2", "name": "Webhook Secret", "age_days": 30, "max_age_days": 90},
    ]
    r = get_rotation_schedule(secrets_list=secrets_list)
    assert r["overdue_count"] == 1
    assert not r["all_current"]
    assert r["schedule"][0]["urgency"] == "critical"
    assert r["schedule"][1]["urgency"] == "ok"
