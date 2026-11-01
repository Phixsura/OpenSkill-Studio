from app.services.app_marketplace_app_deprecation import create_deprecation_notice, build_deprecation_email, check_deprecation_status

def test_create():
    n = create_deprecation_notice(app={"id": "a1", "name": "OldApp"}, sunset_date="2026-12-31", reason="EOL")
    assert n["status"] == "announced"

def test_email():
    notice = {"app_name": "OldApp", "sunset_date": "2026-12-31", "reason": "EOL", "alternative_app_id": "a2"}
    e = build_deprecation_email(notice=notice, install_count=100)
    assert "deprecated" in e["subject"]
    assert "a2" in e["body"]
    assert e["recipients"] == 100

def test_status_announced():
    s = check_deprecation_status(sunset_date="2028-01-01")
    assert s["phase"] == "announced"

def test_status_sunset():
    s = check_deprecation_status(sunset_date="2020-01-01")
    assert s["phase"] == "sunset"
    assert s["days_remaining"] == 0
