from app.services.app_marketplace_app_clipboard_api import generate_install_snippet, generate_share_link

def test_npm():
    r = generate_install_snippet(app_id="a1", package_name="@openskill/auth", manager="npm")
    assert r["command"] == "npm install @openskill/auth"

def test_pip():
    r = generate_install_snippet(app_id="a1", package_name="openskill-auth", manager="pip")
    assert "pip install" in r["command"]

def test_all_managers():
    r = generate_install_snippet(app_id="a1", package_name="pkg")
    assert len(r["all_commands"]) == 5

def test_share():
    r = generate_share_link(resource_type="app", resource_id="auth-sdk")
    assert "/apps/auth-sdk" in r["url"]
    assert r["short_url"].startswith("https://osk.link/")

def test_invalid_type():
    r = generate_share_link(resource_type="widget", resource_id="x")
    assert "error" in r
