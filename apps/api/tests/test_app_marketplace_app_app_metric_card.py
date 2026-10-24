from app.services.app_marketplace_app_app_metric_card import build_metric_card

def test_number():
    r = build_metric_card(label="Users", value=1234)
    assert r["display"] == "1,234"

def test_percent():
    r = build_metric_card(label="Rate", value=98.5, format_fn="percent")
    assert r["display"] == "98.5%"

def test_compact():
    r = build_metric_card(label="Downloads", value=2_500_000, format_fn="compact")
    assert r["display"] == "2.5M"

def test_trend():
    r = build_metric_card(label="Rev", value=150, previous=100)
    assert r["trend"] == "up"
    assert r["change_pct"] == 50.0

def test_trend_down():
    r = build_metric_card(label="Churn", value=5, previous=10)
    assert r["trend"] == "down"
    assert r["change_pct"] == -50.0
