from app.services.app_marketplace_app_version_history import build_version_history

def test_history():
    r = build_version_history(app_id="app1", app_name="TestApp")
    assert r["total_versions"] == 5
    assert r["latest"] == "3.2.0"
    assert r["versions"][0]["version"] == "3.2.0"

def test_major_flag():
    r = build_version_history(app_id="app1", app_name="TestApp")
    majors = [v for v in r["versions"] if v["is_major"]]
    assert len(majors) >= 1
    assert any(v["version"] == "3.0.0" for v in majors)
