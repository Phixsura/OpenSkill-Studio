from app.services.app_marketplace_app_app_app_app_app_app_app_welcome_screen import build_welcome

def test_new():
    r = build_welcome(user_name="Alice", is_new=True)
    assert r["type"] == "new_user"
    assert "Alice" in r["greeting"]
    assert len(r["steps"]) == 3

def test_returning():
    r = build_welcome(user_name="Bob", is_new=False, stats={"new_installs": 5})
    assert r["type"] == "returning"
    assert "Bob" in r["greeting"]
    assert r["stats"]["new_installs"] == 5
