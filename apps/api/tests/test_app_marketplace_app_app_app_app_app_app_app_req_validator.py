from app.services.app_marketplace_app_app_app_app_app_app_app_req_validator import validate_request, sanitize_input

def test_valid():
    r = validate_request(
        {"name": "Alice", "email": "alice@example.com", "age": 25},
        {"name": {"type": "string", "required": True, "min_length": 1},
         "email": {"type": "string", "required": True, "pattern": r"^[\w.+-]+@[\w-]+\.[\w.]+$"},
         "age": {"type": "int"}})
    assert r["valid"]

def test_invalid():
    r = validate_request(
        {"name": "", "email": "not-email"},
        {"name": {"type": "string", "required": True, "min_length": 1},
         "email": {"type": "string", "pattern": r"^[\w.+-]+@[\w-]+\.[\w.]+$"}})
    assert not r["valid"]
    assert len(r["errors"]) == 2

def test_sanitize():
    assert sanitize_input("<script>alert(1)</script>") == "&lt;script&gt;alert(1)&lt;/script&gt;"
    assert len(sanitize_input("a" * 2000, max_length=100)) == 100
