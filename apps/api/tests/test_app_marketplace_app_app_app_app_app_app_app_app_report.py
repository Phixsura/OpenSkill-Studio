from app.services.app_marketplace_app_app_app_app_app_app_app_app_report import create_report, list_reasons

def test_report():
    r = create_report(app_id="bad_app", reporter_id="alice", reason="malware",
                        details="Sends data to unknown server")
    assert r["status"] == "submitted"
    assert r["reason"] == "malware"
    assert r["report_id"].startswith("rpt_")

def test_invalid():
    r = create_report(app_id="x", reporter_id="y", reason="invalid_reason")
    assert "error" in r

def test_reasons():
    assert len(list_reasons()) == 6
