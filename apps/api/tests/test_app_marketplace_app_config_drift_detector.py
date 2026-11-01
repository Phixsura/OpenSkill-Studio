from app.services.app_marketplace_app_config_drift_detector import detect_drift, auto_remediate

def test_no_drift():
    r = detect_drift(expected={"a": 1, "b": 2}, actual={"a": 1, "b": 2})
    assert not r["has_drift"]

def test_drift():
    r = detect_drift(expected={"a": 1, "b": 2}, actual={"a": 1, "b": 99, "c": 3})
    assert r["has_drift"]
    assert r["drift_count"] == 2  # b changed + c extra

def test_missing():
    r = detect_drift(expected={"a": 1, "b": 2}, actual={"a": 1})
    drifts = {d["key"]: d for d in r["drifts"]}
    assert drifts["b"]["type"] == "missing"

def test_remediate():
    drifts = [{"key": "timeout", "expected": 30, "actual": 60}]
    r = auto_remediate(drifts=drifts, policy="reset")
    assert r["actions"][0]["value"] == 30
