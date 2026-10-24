from app.services.app_marketplace_app_app_app_app_app_app_app_error_boundary import create_error_report, build_recovery_ui

def test_report():
    r = create_error_report(error_type="TypeError", message="Cannot read null",
                             component="UserProfile", url="/users/123")
    assert r["severity"] == "critical"
    assert r["fingerprint"]
    assert "null" in r["message"]

def test_recovery():
    err = create_error_report(error_type="NetworkError", message="Fetch failed")
    ui = build_recovery_ui(err)
    assert ui["title"] == "Something went wrong"
    assert len(ui["actions"]) == 3
    assert err["severity"] == "warning"
