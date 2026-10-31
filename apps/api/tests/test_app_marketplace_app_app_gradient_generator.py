from app.services.app_marketplace_app_app_gradient_generator import generate_gradient, list_presets

def test_basic():
    r = generate_gradient(from_color="#FF0000", to_color="#0000FF")
    assert r["valid"]
    assert "linear-gradient" in r["css"]
    assert len(r["stops"]) == 2

def test_via():
    r = generate_gradient(from_color="#FF0000", to_color="#0000FF", via_color="#00FF00")
    assert len(r["stops"]) == 3

def test_invalid():
    r = generate_gradient(from_color="red", to_color="#0000FF")
    assert not r["valid"]

def test_presets():
    p = list_presets()
    assert len(p) == 6
    assert all("css" in x for x in p)
