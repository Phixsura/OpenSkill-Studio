from app.services.app_marketplace_app_app_app_app_app_app_app_kpi_cards import build_kpi_cards

def test_kpis():
    cards = build_kpi_cards({
        "mrr": 50000, "mrr_prev": 45000,
        "dau": 3500, "dau_prev": 3200,
        "churn": 2.5, "churn_prev": 3.0,
        "uptime": 99.95,
    })
    assert len(cards) == 4
    mrr = next(c for c in cards if c["key"] == "mrr")
    assert mrr["display"] == "$50,000"
    assert mrr["positive"]  # up is good for MRR
    churn = next(c for c in cards if c["key"] == "churn")
    assert churn["positive"]  # down is good for churn
    assert churn["trend"] == "down"
