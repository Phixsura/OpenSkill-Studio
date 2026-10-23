from app.services.app_marketplace_app_app_app_app_app_app_app_key_rotation import (
    create_rotation_schedule, rotate_key, check_rotation_needed,
)

def test_rotate():
    s = create_rotation_schedule("prod_key", 90)
    r = rotate_key(s)
    assert r["rotated"]
    assert s["rotation_count"] == 1
    assert r["new_key_prefix"].startswith("sk_")

def test_check():
    now = 1000000.0
    schedules = [
        {"key_name": "old", "next_rotation": now - 100, "rotation_days": 90},
        {"key_name": "soon", "next_rotation": now + 86400 * 3, "rotation_days": 90},
        {"key_name": "fine", "next_rotation": now + 86400 * 30, "rotation_days": 90},
    ]
    r = check_rotation_needed(schedules, now=now)
    assert r["due_count"] == 1
    assert "old" in r["due_keys"]
    assert r["upcoming_count"] == 1
    assert r["action_needed"]
