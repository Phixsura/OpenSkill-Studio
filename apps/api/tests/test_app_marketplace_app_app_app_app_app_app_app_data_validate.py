from app.services.app_marketplace_app_app_app_app_app_app_app_data_validate import validate_record, validate_batch

def test_valid():
    r = validate_record({"name": "Alice", "age": 25},
        [{"field": "name", "rule": "required"}, {"field": "age", "rule": "min", "value": 0}])
    assert r["valid"]

def test_errors():
    r = validate_record({"age": -1},
        [{"field": "name", "rule": "required"}, {"field": "age", "rule": "min", "value": 0}])
    assert not r["valid"]
    assert r["error_count"] == 2

def test_batch():
    records = [{"name": "A", "age": 20}, {"age": 10}, {"name": "C", "age": -1}]
    r = validate_batch(records, [{"field": "name", "rule": "required"}, {"field": "age", "rule": "min", "value": 0}])
    assert r["valid"] == 1
    assert r["pass_rate"] == 33
