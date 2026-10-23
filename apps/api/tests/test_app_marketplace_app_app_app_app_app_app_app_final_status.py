from app.services.app_marketplace_app_app_app_app_app_app_app_final_status import build_system_status

def test_status():
    r = build_system_status()
    assert "Operational" in r["overall"]
    assert r["overall_icon"] == "🟢"
    assert r["service_count"] == 10
    assert r["avg_uptime"] > 99
    assert "None" in r["last_incident"]
