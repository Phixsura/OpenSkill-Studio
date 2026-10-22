from app.services.app_abuse_report import submit_report, get_reports, get_report_count, should_auto_suspend, REPORT_REASONS

def test_submit():
    r = submit_report(app_id="ar1", reporter_id="u1", reason="spam", details="Looks like spam")
    assert r is not None
    assert r["status"] == "pending"

def test_invalid_reason():
    assert submit_report(app_id="ar2", reporter_id="u1", reason="invalid") is None

def test_duplicate():
    submit_report(app_id="ar3", reporter_id="u1", reason="spam")
    assert submit_report(app_id="ar3", reporter_id="u1", reason="malware") is None

def test_count():
    submit_report(app_id="ar4", reporter_id="u1", reason="spam")
    submit_report(app_id="ar4", reporter_id="u2", reason="spam")
    assert get_report_count("ar4") == 2

def test_auto_suspend():
    for i in range(5):
        submit_report(app_id="ar5", reporter_id=f"u{i}", reason="malware")
    assert should_auto_suspend("ar5") is True

def test_reasons():
    assert len(REPORT_REASONS) >= 5
