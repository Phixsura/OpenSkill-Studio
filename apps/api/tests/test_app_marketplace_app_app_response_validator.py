from app.services.app_marketplace_app_app_response_validator import validate_response, build_validation_report

def test_valid():
    schema = {"id": {"type": "string", "required": True}, "count": {"type": "integer"}}
    r = validate_response(response={"id": "abc", "count": 5}, schema=schema)
    assert r["valid"]

def test_missing_required():
    r = validate_response(response={}, schema={"id": {"type": "string", "required": True}})
    assert not r["valid"]

def test_wrong_type():
    r = validate_response(response={"id": 123}, schema={"id": {"type": "string"}})
    assert not r["valid"]

def test_report():
    schema = {"name": {"type": "string", "required": True}}
    responses = [{"name": "ok"}, {"name": 123}, {}]
    r = build_validation_report(responses=responses, schema=schema)
    assert r["valid"] == 1
    assert r["pass_rate"] == 33.3
