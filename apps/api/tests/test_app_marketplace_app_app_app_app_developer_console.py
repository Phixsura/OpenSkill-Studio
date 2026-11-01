from app.services.app_marketplace_app_app_app_app_developer_console import build_developer_console

def test_console():
    user = {"name": "Alice"}
    org = {"name": "Acme", "plan": "pro", "member_count": 5}
    apps = [{"installs": 10000, "api_calls": 50000}, {"installs": 5000, "api_calls": 20000}]
    r = build_developer_console(user=user, org=org, apps=apps, notifications=3)
    assert "Alice" in r["greeting"]
    assert len(r["console_sections"]) == 8
    assert r["stats"][0]["value"] == 2
    assert r["stats"][1]["display"] == "15,000"
    assert r["org"]["plan"] == "pro"
    assert r["notifications"] == 3
