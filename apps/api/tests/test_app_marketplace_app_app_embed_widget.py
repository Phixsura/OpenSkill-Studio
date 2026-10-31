from app.services.app_marketplace_app_app_embed_widget import generate_embed_code, get_embed_analytics

def test_embed():
    r = generate_embed_code(app_id="auth-sdk", app_name="Auth SDK", theme="dark")
    assert "iframe" in r["iframe_code"]
    assert "theme=dark" in r["iframe_code"]
    assert 'data-app="auth-sdk"' in r["script_code"]

def test_xss():
    r = generate_embed_code(app_id='"><script>', app_name="X")
    assert "<script>" not in r["iframe_code"]

def test_invalid_theme():
    r = generate_embed_code(app_id="x", app_name="X", theme="neon")
    assert "error" in r

def test_analytics():
    embeds = [{"domain": "blog.com", "views": 500, "clicks": 25},
              {"domain": "docs.com", "views": 300, "clicks": 15}]
    r = get_embed_analytics(embeds=embeds)
    assert r["total_views"] == 800
    assert r["ctr"] == 5.0
    assert r["top_domains"][0]["domain"] == "blog.com"
