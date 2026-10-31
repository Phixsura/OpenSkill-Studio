from app.services.app_marketplace_306k_14k_milestone import celebrate_306k_14k
def test_double():
    r = celebrate_306k_14k()
    assert "306,000" in r["milestones"][0]
    assert "14,000" in r["milestones"][1]
