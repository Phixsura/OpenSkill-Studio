from app.services.app_marketplace_app_playground_sandbox import create_sandbox, list_active_sandboxes

def test_create():
    r = create_sandbox(app_id="a1", user_id="u1", template="react", timeout_min=60)
    assert r["sandbox_id"].startswith("sb_")
    assert r["template"] == "react"
    assert r["status"] == "running"

def test_invalid_template():
    r = create_sandbox(app_id="a1", user_id="u1", template="rust")
    assert "error" in r

def test_too_long():
    r = create_sandbox(app_id="a1", user_id="u1", timeout_min=200)
    assert "error" in r

def test_list():
    r = list_active_sandboxes(user_id="u1")
    assert r["total"] == 1
    assert r["max_concurrent"] == 3
