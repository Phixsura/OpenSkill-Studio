from app.services.app_marketplace_app_app_app_app_app_app_app_auto_triage import auto_triage, triage_stats

def test_triage():
    r = auto_triage("database", ["connection_timeout", "query_slow"])
    assert r["triaged"]
    assert r["assigned_team"] == "data-eng"
    assert r["severity"] == "critical"
    assert r["escalate"]

def test_unknown():
    r = auto_triage("unknown_thing", [])
    assert not r["triaged"]
    assert r["assigned_team"] == "oncall"

def test_stats():
    triages = [auto_triage("database", []), auto_triage("api_error", []), auto_triage("ui", [])]
    r = triage_stats(triages)
    assert r["auto_triaged"] == 3
    assert r["by_team"]["data-eng"] == 1
