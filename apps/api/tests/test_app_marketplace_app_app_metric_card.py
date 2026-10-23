from app.services.app_marketplace_app_app_metric_card import build_metric_card

def test_with_change():
    r = build_metric_card(label="Users", value=1500, previous=1200, icon="👥")
    assert r["change"] == 300
    assert r["change_pct"] == 25.0
    assert r["trend"] == "up"

def test_no_previous():
    r = build_metric_card(label="Revenue", value=5000, format_type="currency")
    assert r["change"] is None
    assert r["trend"] is None

def test_down():
    r = build_metric_card(label="Errors", value=10, previous=20)
    assert r["trend"] == "down"
    assert r["change"] == -10
