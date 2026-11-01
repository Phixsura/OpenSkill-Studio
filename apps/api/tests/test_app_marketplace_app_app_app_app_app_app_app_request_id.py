from app.services.app_marketplace_app_app_app_app_app_app_app_request_id import generate_request_id, extract_timestamp, validate_request_id

def test_generate():
    r = generate_request_id("req")
    assert r["request_id"].startswith("req_")
    assert r["traceable"]
    r2 = generate_request_id("api", include_timestamp=False)
    assert r2["request_id"].startswith("api_")

def test_extract():
    r = generate_request_id()
    e = extract_timestamp(r["request_id"])
    assert e["extracted"]
    assert e["timestamp"] > 0

def test_validate():
    r = generate_request_id()
    v = validate_request_id(r["request_id"])
    assert v["valid"]
    v2 = validate_request_id("bad")
    assert not v2["valid"]
