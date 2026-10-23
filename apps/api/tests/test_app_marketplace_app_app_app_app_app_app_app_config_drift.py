from app.services.app_marketplace_app_app_app_app_app_app_app_config_drift import detect_drift, suggest_fixes

def test_drift():
    r = detect_drift({
        "production": {"db_host": "prod-db", "cache": "redis", "debug": False},
        "staging": {"db_host": "stg-db", "cache": "redis", "debug": True},
        "development": {"db_host": "localhost", "cache": "memory", "debug": True},
    })
    assert r["has_drift"]
    assert r["drift_count"] == 3  # db_host, cache, debug all differ

def test_fixes():
    drifts = [{"key": "debug", "values": {"production": False, "staging": True}}]
    fixes = suggest_fixes(drifts, "production")
    assert len(fixes) == 1
    assert fixes[0]["environment"] == "staging"
    assert fixes[0]["expected"] is False
