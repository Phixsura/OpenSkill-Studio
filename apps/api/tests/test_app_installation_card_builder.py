from app.services.app_installation_card_builder import build_installation_card

def test_card():
    c = build_installation_card(
        installation={"id": "i1", "status": "active", "version": "2.0", "created_at": "2026-01"},
        app={"name": "App", "slug": "app", "category": "connector"}, health_score=95)
    assert c["app_name"] == "App"
    assert c["health_status"] == "healthy"

def test_degraded():
    c = build_installation_card(installation={"id": "i2"}, app={"name": "X"}, health_score=85)
    assert c["health_status"] == "degraded"
