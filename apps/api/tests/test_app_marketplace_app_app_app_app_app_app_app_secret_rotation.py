from app.services.app_marketplace_app_app_app_app_app_app_app_secret_rotation import (
    create_rotation_policy, check_rotation_status, rotate_secret,
)

def test_policy_and_status():
    p = create_rotation_policy("API_KEY", rotation_days=90, notify_days=14)
    now = p["created_at"] + 86400 * 80  # 80 days later
    r = check_rotation_status(p, p["created_at"], now=now)
    assert r["status"] == "warning"
    assert r["due_in_days"] == 10.0
    assert not r["needs_rotation"]

def test_overdue():
    p = create_rotation_policy("DB_PASS", rotation_days=30)
    r = check_rotation_status(p, p["created_at"], now=p["created_at"] + 86400 * 35)
    assert r["status"] == "overdue"
    assert r["needs_rotation"]

def test_rotate():
    r = rotate_secret(32)
    assert len(r["new_secret"]) > 20
    assert r["rotated_at"] > 0
