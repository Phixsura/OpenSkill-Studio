from app.services.app_developer_app_clone import clone_app

ORIGINAL = {"id": "a1", "name": "Original", "slug": "original", "status": "published",
            "category": "connector", "oauth_client_id": "xxx", "install_count": 100}

def test_clone_new_identity():
    c = clone_app(ORIGINAL, new_name="Clone", new_slug="clone")
    assert c["id"] != "a1"
    assert c["name"] == "Clone"
    assert c["slug"] == "clone"

def test_clone_reset_status():
    c = clone_app(ORIGINAL, new_name="C", new_slug="c")
    assert c["status"] == "draft"
    assert c["visibility"] == "private"
    assert c["install_count"] == 0

def test_clone_removes_oauth():
    c = clone_app(ORIGINAL, new_name="C", new_slug="c")
    assert "oauth_client_id" not in c

def test_clone_keeps_category():
    c = clone_app(ORIGINAL, new_name="C", new_slug="c")
    assert c["category"] == "connector"

def test_no_mutation():
    clone_app(ORIGINAL, new_name="C", new_slug="c")
    assert ORIGINAL["name"] == "Original"
