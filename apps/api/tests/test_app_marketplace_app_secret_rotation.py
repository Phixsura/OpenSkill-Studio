from app.services.app_marketplace_app_secret_rotation import generate_secret, create_rotation_schedule, rotate_secret

def test_generate():
    s = generate_secret()
    assert len(s) > 20

def test_schedule_overdue():
    r = create_rotation_schedule(secret_name="api_key", rotation_days=30, last_rotated="2020-01-01T00:00:00Z")
    assert r["overdue"]

def test_schedule_fresh():
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc).isoformat()
    r = create_rotation_schedule(secret_name="api_key", rotation_days=30, last_rotated=now)
    assert not r["overdue"]

def test_schedule_invalid():
    r = create_rotation_schedule(secret_name="x", rotation_days=0)
    assert r["error"]

def test_rotate():
    r = rotate_secret(secret_name="api_key", old_hash="abc")
    assert len(r["new_hash"]) == 64
    assert r["grace_period_hours"] == 24
