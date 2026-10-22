from app.services.app_marketplace_app_stats_card import build_app_stats_card

def test_card():
    c = build_app_stats_card(installs=100, executions=5000, webhooks=2000, health=95, rating=4.5, reviews=20)
    assert len(c["metrics"]) == 6
    assert c["metrics"][0]["value"] == 100

def test_low_health():
    c = build_app_stats_card(installs=0, executions=0, webhooks=0, health=50, rating=0, reviews=0)
    assert c["metrics"][3]["icon"] == "⚠️"
