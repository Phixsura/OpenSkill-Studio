from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_metric_card import fleet_metric_cardinality
def test_cardinality():
    r = fleet_metric_cardinality([{"series_count": 500000}, {"series_count": 600000}])
    assert r["total_series"] == 1100000
    assert r["warning"]
    assert r["high_cardinality"] == 2
