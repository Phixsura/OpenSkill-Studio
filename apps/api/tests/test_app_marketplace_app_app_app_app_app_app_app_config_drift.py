from app.services.app_marketplace_app_app_app_app_app_app_app_config_drift import detect_drift, summarize_drift

def test_drift():
    expected = {"replicas": 3, "image": "app:v2", "env": {"DB_HOST": "db.prod", "LOG_LEVEL": "info"}}
    actual = {"replicas": 2, "image": "app:v2", "env": {"DB_HOST": "db.prod", "LOG_LEVEL": "debug", "DEBUG": "true"}}
    diffs = detect_drift(expected, actual)
    assert len(diffs) == 3  # replicas changed, LOG_LEVEL changed, DEBUG extra
    s = summarize_drift(diffs)
    assert s["has_drift"]
    assert s["by_type"]["changed"] == 2
    assert s["by_type"]["extra"] == 1

def test_no_drift():
    d = detect_drift({"a": 1}, {"a": 1})
    assert len(d) == 0
    s = summarize_drift(d)
    assert s["severity"] == "clean"
