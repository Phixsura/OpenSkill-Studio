from app.services.app_marketplace_auth_page import build_login_page, build_register_page, build_password_reset_page

def test_login():
    p = build_login_page(providers=["github", "google", "email"], redirect_url="/dashboard")
    assert p["page_type"] == "login"
    assert len(p["providers"]) == 3
    assert p["redirect_url"] == "/dashboard"

def test_register():
    p = build_register_page(providers=["github"], plans=[{"name": "free"}, {"name": "pro"}])
    assert len(p["plans"]) == 2
    assert "display_name" in p["fields"]

def test_reset():
    p = build_password_reset_page()
    assert p["page_type"] == "password_reset"
    assert "email" in p["fields"]
