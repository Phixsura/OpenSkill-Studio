from app.services.app_marketplace_app_app_app_app_app_app_app_cardinality import analyze_cardinality, label_analysis

def test_cardinality():
    r = analyze_cardinality([
        {"name": "http_requests", "series_count": 50000, "label_count": 5},
        {"name": "cpu_usage", "series_count": 100, "label_count": 2},
    ])
    assert r["high_card_count"] == 1
    assert r["total_series"] == 50100

def test_labels():
    r = label_analysis({"name": "http_requests", "labels": {"method": 5, "path": 50000, "status": 10}})
    assert r["high_card_labels"] == 1  # path has >1000
    assert r["total_labels"] == 3
