from app.services.app_marketplace_app_app_copy_generator import generate_copy, build_copy_set

def test_hero():
    r = generate_copy(template_id="hero", variables={"name": "SuperApp", "tagline": "Do more", "benefit": "Save time"})
    assert "SuperApp" in r["text"]
    assert "Do more" in r["text"]

def test_unknown_template():
    r = generate_copy(template_id="nonexistent", variables={})
    assert "error" in r

def test_missing_var():
    r = generate_copy(template_id="hero", variables={"name": "X"})
    assert "error" in r

def test_copy_set():
    r = build_copy_set(app_name="MyApp", tagline="Build faster", benefit="Ship today")
    assert r["count"] == 4
    assert "hero" in r["copies"]
    assert "MyApp" in r["copies"]["hero"]
