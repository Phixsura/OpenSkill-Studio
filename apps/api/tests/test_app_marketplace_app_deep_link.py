from app.services.app_marketplace_app_deep_link import generate_deep_link, resolve_deep_link

def test_generate():
    r = generate_deep_link(app_id="app123", action="install", params={"ref": "email"})
    assert "openskill://marketplace/app/app123" in r["deep_link"]
    assert "action=install" in r["deep_link"]
    assert r["short_link"].startswith("https://osk.link/")
    assert r["web_fallback"].endswith("/apps/app123")

def test_resolve():
    r = resolve_deep_link(url="openskill://marketplace/app/app123?action=install&ref=email")
    assert r["resolved"]
    assert r["action"] == "install"
    assert "app123" in r["path_segments"]

def test_resolve_invalid():
    r = resolve_deep_link(url="https://example.com/foo")
    assert not r["resolved"]
