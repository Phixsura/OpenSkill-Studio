from app.services.app_webhook_secret_rotation import create_rotation, is_in_grace, should_accept_old_secret

def test_create():
    r = create_rotation(current_secret_id="s1")
    assert r["old_secret_id"] == "s1"
    assert len(r["new_secret"]) > 10
    assert r["status"] == "active"

def test_in_grace():
    r = create_rotation(current_secret_id="s1", grace_hours=24)
    assert is_in_grace(r) is True

def test_should_accept_old():
    r = create_rotation(current_secret_id="s1")
    assert should_accept_old_secret(r) is True

def test_should_not_accept_none():
    assert should_accept_old_secret(None) is False
