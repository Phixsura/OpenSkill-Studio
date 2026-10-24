from app.services.app_marketplace_app_app_app_app_app_app_app_dev_survey import analyze_survey

def test_survey():
    r = analyze_survey([
        {"scores": {"docs": 4, "sdk": 5, "support": 3}, "nps": 9},
        {"scores": {"docs": 3, "sdk": 4, "support": 4}, "nps": 7},
        {"scores": {"docs": 5, "sdk": 5, "support": 5}, "nps": 10},
    ])
    assert r["respondents"] == 3
    assert r["categories"]["sdk"]["avg"] == 4.7
    assert r["nps"] > 0
