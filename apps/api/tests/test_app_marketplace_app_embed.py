from app.services.app_marketplace_app_embed import generate_embed_code, generate_install_button, validate_embed_domain

def test_embed():
    r = generate_embed_code(app={"id": "a1", "name": "MyApp", "slug": "my-app"})
    assert "iframe" in r["iframe"]
    assert "my-app" in r["iframe"]
    assert "badge" in r

def test_install_button():
    btn = generate_install_button(app={"name": "App", "slug": "app"})
    assert "Install App" in btn
    assert "2563eb" in btn

def test_minimal_button():
    btn = generate_install_button(app={"name": "App", "slug": "app"}, style="minimal")
    assert "style" not in btn

def test_domain_ok():
    assert validate_embed_domain(domain="example.com", allowed_domains=["example.com"])

def test_domain_wildcard():
    assert validate_embed_domain(domain="any.com", allowed_domains=["*"])

def test_domain_rejected():
    assert not validate_embed_domain(domain="evil.com", allowed_domains=["good.com"])
