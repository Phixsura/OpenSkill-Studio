from app.services.app_marketplace_app_cloning import clone_app, validate_clone_permissions

def test_clone():
    c = clone_app(source_app={"id": "a1", "category": "connector", "description": "D", "default_config": {"k": "v"}},
                   new_name="My Fork", new_slug="my-fork", developer_id="d1")
    assert c["status"] == "draft"
    assert c["cloned_from"] == "a1"
    assert c["default_config"] == {"k": "v"}

def test_clone_no_config():
    c = clone_app(source_app={"id": "a1"}, new_name="F", new_slug="f", developer_id="d1", include_config=False)
    assert "default_config" not in c

def test_validate_ok():
    r = validate_clone_permissions(source_app={"status": "published"}, developer_id="d1")
    assert r["allowed"]

def test_validate_no_clone():
    r = validate_clone_permissions(source_app={"status": "published", "allow_cloning": False}, developer_id="d1")
    assert not r["allowed"]

def test_validate_draft():
    r = validate_clone_permissions(source_app={"status": "draft"}, developer_id="d1")
    assert not r["allowed"]
