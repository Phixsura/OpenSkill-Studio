from app.services.app_marketplace_app_app_app_app_app_app_app_metric_card import build_metric_card, build_metric_row

def test_card():
    r = build_metric_card(label="Revenue", value=45000, format_type="currency", previous=40000, icon="💰")
    assert r["display"] == "$45,000"
    assert r["trend"] == "up"
    assert r["delta"] == 12.5

def test_compact():
    r = build_metric_card(label="Users", value=2500000, format_type="compact")
    assert r["display"] == "2.5M"

def test_row():
    row = build_metric_row([
        {"label": "A", "value": 100}, {"label": "B", "value": 200},
    ])
    assert len(row) == 2
