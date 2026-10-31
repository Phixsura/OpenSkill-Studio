from app.services.app_marketplace_app_app_text_input import build_input_config

def test_basic():
    r = build_input_config(name="email", label="Email", input_type="email",
        placeholder="you@example.com", required=True)
    assert r["name"] == "email"
    assert r["type"] == "email"
    assert r["required"]

def test_with_validation():
    r = build_input_config(name="username", label="Username", min_length=3, max_length=20,
        pattern="^[a-z0-9_]+$", help_text="Lowercase, numbers, underscores")
    assert r["min_length"] == 3
    assert r["help_text"] is not None

def test_invalid_type():
    r = build_input_config(name="x", label="X", input_type="color")
    assert "error" in r
