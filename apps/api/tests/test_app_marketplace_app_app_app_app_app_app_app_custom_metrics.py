from app.services.app_marketplace_app_app_app_app_app_app_app_custom_metrics import CustomMetricsRegistry

def test_record_query():
    cmr = CustomMetricsRegistry()
    cmr.register("order_value", "USD", "Order total value")
    cmr.record("order_value", 50)
    cmr.record("order_value", 100)
    cmr.record("order_value", 150)
    r = cmr.query("order_value")
    assert r["count"] == 3
    assert r["avg"] == 100
    assert r["sum"] == 300
    assert r["unit"] == "USD"

def test_list():
    cmr = CustomMetricsRegistry()
    cmr.register("a", "ms")
    cmr.register("b", "count")
    cmr.record("a", 1)
    assert len(cmr.list_metrics()) == 2
