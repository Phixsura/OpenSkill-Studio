from app.services.app_marketplace_app_app_app_app_app_app_app_custom_metrics import CustomMetricsRegistry

def test_counter():
    r = CustomMetricsRegistry()
    r.define("orders_total", metric_type="counter", unit="count")
    r.record("orders_total", 5)
    r.record("orders_total", 3)
    q = r.query("orders_total")
    assert q["current"] == 8
    assert q["count"] == 2

def test_gauge():
    r = CustomMetricsRegistry()
    r.define("cpu_temp", metric_type="gauge", unit="°C")
    r.record("cpu_temp", 65)
    r.record("cpu_temp", 72)
    q = r.query("cpu_temp")
    assert q["current"] == 72
    assert q["avg"] == 68.5

def test_list():
    r = CustomMetricsRegistry()
    r.define("a", metric_type="counter")
    r.define("b", metric_type="gauge")
    assert len(r.list_metrics()) == 2
