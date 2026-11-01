from app.services.app_marketplace_app_app_api_key_rotation import rotate_key, check_rotation_status

def test_rotate():
    r = rotate_key(current_prefix="osk_old1", grace_period_hours=48)
    assert r["new_key"].startswith("osk_")
    assert r["old_prefix"] == "osk_old1"
    assert len(r["new_key"]) == 52

def test_in_grace():
    r = check_rotation_status(rotated_at="2026-01-01T00:00:00+00:00",
                               grace_until="2099-01-01T00:00:00+00:00")
    assert r["old_key_active"]
    assert r["status"] == "in_grace_period"

def test_grace_expired():
    r = check_rotation_status(rotated_at="2020-01-01T00:00:00+00:00",
                               grace_until="2020-01-02T00:00:00+00:00")
    assert r["grace_expired"]
    assert r["status"] == "completed"
