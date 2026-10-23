from app.services.app_marketplace_app_app_logo_placeholder import generate_placeholder

def test_basic():
    r = generate_placeholder(app_name="Auth SDK", size=64)
    assert r["initials"] == "AS"
    assert r["size"] == 64
    assert r["font_size"] == 32
    assert "from-" in r["gradient"]

def test_single_word():
    r = generate_placeholder(app_name="Dashboard")
    assert r["initials"] == "D"

def test_deterministic():
    r1 = generate_placeholder(app_name="Test App")
    r2 = generate_placeholder(app_name="Test App")
    assert r1["gradient"] == r2["gradient"]
