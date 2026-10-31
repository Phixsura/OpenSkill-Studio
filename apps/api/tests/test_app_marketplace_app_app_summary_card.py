from app.services.app_marketplace_app_app_summary_card import build_summary_card

def test_card():
    metrics = [
        {"label": "Revenue", "value": 12500, "format": "currency"},
        {"label": "Users", "value": 5400, "format": "compact"},
        {"label": "Rating", "value": 4.8},
    ]
    r = build_summary_card(title="Monthly Summary", metrics=metrics, icon="📈")
    assert r["title"] == "Monthly Summary"
    assert r["metrics"][0]["display"] == "$12,500.00"
    assert r["metrics"][1]["display"] == "5.4K"
    assert r["metric_count"] == 3
