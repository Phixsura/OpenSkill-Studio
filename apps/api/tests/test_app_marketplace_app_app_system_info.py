from app.services.app_marketplace_app_app_system_info import get_system_info, build_about_page

def test_system_info():
    r = get_system_info()
    assert "python_version" in r
    assert r["api_version"] == "2.0.0"

def test_about_page():
    r = build_about_page(app_name="Test App", version="3.0.0")
    assert r["app_name"] == "Test App"
    assert len(r["components"]) == 4
    assert all(c["status"] == "operational" for c in r["components"])
    assert "/docs" in r["links"]["docs"]
