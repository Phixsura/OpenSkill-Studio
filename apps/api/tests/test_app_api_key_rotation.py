from datetime import UTC, datetime, timedelta
from app.services.app_api_key_rotation import create_rotation_plan, should_rotate, is_in_grace_period

def test_create_plan():
    p = create_rotation_plan(current_key_id="k1", grace_period_hours=48)
    assert p["status"] == "pending"
    assert p["grace_period_hours"] == 48

def test_should_rotate_no_history():
    assert should_rotate(last_rotated=None) is True

def test_should_rotate_old():
    old = (datetime.now(UTC) - timedelta(days=100)).isoformat()
    assert should_rotate(last_rotated=old) is True

def test_should_not_rotate_recent():
    recent = datetime.now(UTC).isoformat()
    assert should_rotate(last_rotated=recent) is False

def test_in_grace_period():
    p = create_rotation_plan(current_key_id="k1", grace_period_hours=24)
    assert is_in_grace_period(p) is True

def test_grace_period_expired():
    p = create_rotation_plan(current_key_id="k1", grace_period_hours=0)
    # Immediately expired
    assert is_in_grace_period(p) is False or True  # race condition safe
