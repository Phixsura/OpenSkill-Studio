from app.services.app_marketplace_app_app_app_app_app_app_app_resp_valid import validate_response, batch_validate

def test_valid():
    r = validate_response(
        {"status": 200, "body": {"id": "u1", "name": "Alice", "tags": ["admin"]}},
        {"status": 200, "fields": {"id": {"type": "string", "required": True},
                                    "name": {"type": "string"}, "tags": {"type": "array"}}})
    assert r["valid"]

def test_invalid():
    r = validate_response(
        {"status": 200, "body": {"id": 123}},
        {"status": 200, "fields": {"id": {"type": "string", "required": True},
                                    "name": {"type": "string", "required": True}}})
    assert not r["valid"]
    assert len(r["errors"]) == 2

def test_batch():
    schema = {"status": 200, "fields": {"id": {"type": "string", "required": True}}}
    r = batch_validate([
        {"status": 200, "body": {"id": "u1"}},
        {"status": 200, "body": {}},
    ], schema)
    assert r["valid"] == 1
    assert r["validity_pct"] == 50.0
