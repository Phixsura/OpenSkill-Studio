from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_metrics_srv import fleet_metrics_server
def test_ms():
    r = fleet_metrics_server([{"healthy": True, "nodes_scraped": 10, "scrape_interval_sec": 15}])
    assert r["nodes_scraped"] == 10
    assert r["all_healthy"]
