from app.services.app_marketplace_app_app_embed_code import generate_embed

def test_embed():
    r = generate_embed(app_id="app_123", base_url="https://marketplace.openskill.dev")
    assert "iframe" in r
    assert "app_123" in r["iframe"]
    assert "script" in r
    assert r["theme"] == "light"

def test_dark_theme():
    r = generate_embed(app_id="x", base_url="https://example.com", theme="dark", width=600)
    assert "dark" in r["widget_url"]
    assert r["width"] == 600

def test_bad_url():
    r = generate_embed(app_id="x", base_url="javascript:alert(1)")
    assert "error" in r
