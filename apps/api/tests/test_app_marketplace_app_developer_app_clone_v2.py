from app.services.app_marketplace_app_developer_app_clone_v2 import deep_clone_app, get_clone_diff

def test_clone():
    source = {"id": "a1", "name": "Original", "category": "connector", "default_config": {"k": "v"}, "permissions": ["read"]}
    c = deep_clone_app(source=source, new_name="Fork", new_slug="fork", developer_id="d2")
    assert c["name"] == "Fork"
    assert c["cloned_from"] == "a1"
    assert c["config"] == {"k": "v"}

def test_clone_no_config():
    source = {"id": "a1", "name": "X", "default_config": {"secret": "val"}}
    c = deep_clone_app(source=source, new_name="Y", new_slug="y", developer_id="d2", include_config=False)
    assert "config" not in c

def test_diff():
    source = {"name": "A", "slug": "a", "developer_id": "d1"}
    clone = {"name": "B", "slug": "b", "developer_id": "d2"}
    d = get_clone_diff(source=source, clone=clone)
    assert len(d["diffs"]) == 3
