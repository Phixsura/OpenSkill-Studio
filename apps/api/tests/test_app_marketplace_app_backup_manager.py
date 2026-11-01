from app.services.app_marketplace_app_backup_manager import create_backup, list_backups

def test_create():
    r = create_backup(app_id="a1", backup_type="full")
    assert r["backup_id"].startswith("bak_")
    assert r["status"] == "completed"
    assert len(r["components"]) == 4

def test_config_only():
    r = create_backup(app_id="a1", backup_type="config_only", include=["config"])
    assert r["components"] == ["config"]
    assert r["size_mb"] == 128

def test_invalid():
    r = create_backup(app_id="a1", backup_type="magic")
    assert "error" in r

def test_list():
    r = list_backups(app_id="a1")
    assert r["total"] == 2
    assert r["total_size_mb"] == 576
