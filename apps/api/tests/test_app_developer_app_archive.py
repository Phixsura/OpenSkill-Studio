from app.services.app_developer_app_archive import archive_app, restore_app, get_archived, is_archived

def test_archive():
    a = archive_app(app_id="arc1", app_data={"name": "Old App", "developer_id": "d1"}, reason="deprecated")
    assert a["archive_reason"] == "deprecated"
    assert is_archived("arc1") is True

def test_restore():
    archive_app(app_id="arc2", app_data={"name": "X"})
    restored = restore_app("arc2")
    assert restored is not None
    assert is_archived("arc2") is False

def test_get_archived():
    archive_app(app_id="arc3", app_data={"developer_id": "d2"})
    assert len(get_archived("d2")) >= 1

def test_restore_missing():
    assert restore_app("nonexist") is None
