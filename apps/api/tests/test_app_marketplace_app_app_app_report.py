from app.services.app_marketplace_app_app_app_report import create_report, build_report_queue

def test_create():
    r = create_report(app_id="a1", reporter_id="u1", reason="spam", details="This app is spam")
    assert r["report_id"].startswith("rpt_")
    assert r["severity"] == "medium"
    assert r["status"] == "open"

def test_invalid_reason():
    r = create_report(app_id="a1", reporter_id="u1", reason="invalid")
    assert "error" in r

def test_queue():
    reports = [
        {"status": "open", "severity": "critical"},
        {"status": "open", "severity": "low"},
        {"status": "resolved", "severity": "medium"},
    ]
    r = build_report_queue(reports=reports)
    assert r["open"] == 2
    assert r["has_critical"]
