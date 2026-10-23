from app.services.app_marketplace_app_app_app_app_app_app_app_embed_widget import generate_embed_code, list_embed_styles

def test_embed():
    r = generate_embed_code(app_id="myapp", app_name="My App", style="badge", theme="dark")
    assert "embed/myapp" in r["embed_url"]
    assert "badge" in r["embed_url"]
    assert "dark" in r["embed_url"]
    assert "<iframe" in r["iframe_code"]
    assert r["width"] == "200"

def test_styles():
    assert len(list_embed_styles()) == 3
