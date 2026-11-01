from app.services.app_marketplace_app_backup_restore import create_backup, validate_backup, restore_from_backup

def test_create():
    b = create_backup(app_id="a1", config={"timeout": 30}, secrets_count=3,
                       webhooks=[{"url": "https://x.com"}], metadata={"version": "1.0"})
    assert b["status"] == "completed"
    assert b["secrets_included"] is False
    assert len(b["checksum"]) == 16

def test_validate_ok():
    r = validate_backup(backup={"app_id": "a1", "checksum": "abc123"}, current_app_id="a1")
    assert r["valid"]

def test_validate_wrong_app():
    r = validate_backup(backup={"app_id": "a2", "checksum": "abc"}, current_app_id="a1")
    assert not r["valid"]

def test_restore():
    r = restore_from_backup(backup={"backup_id": "bak_a1_abc", "secrets_count": 2}, target_app_id="a1")
    assert r["status"] == "restored"
    assert len(r["warnings"]) == 1

def test_restore_no_secrets():
    r = restore_from_backup(backup={"backup_id": "bak_a1_abc", "secrets_count": 0}, target_app_id="a1")
    assert len(r["warnings"]) == 0
