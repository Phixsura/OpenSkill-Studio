from app.services.app_marketplace_extension_metrics_aggregator import MetricsAggregator


def test_record_and_totals():
    ma = MetricsAggregator()
    ma.record("latency", 45.0, "2026-10-25T10:00:00")
    ma.record("latency", 55.0, "2026-10-25T10:01:00")
    ma.record("latency", 50.0, "2026-10-25T10:02:00")
    totals = ma.get_totals("latency")
    assert totals["count"] == 3
    assert totals["avg"] == 50.0
    assert totals["min"] == 45.0
    assert totals["max"] == 55.0


def test_daily_aggregation():
    ma = MetricsAggregator()
    ma.record("requests", 100, "2026-10-25T10:00:00")
    ma.record("requests", 200, "2026-10-25T14:00:00")
    ma.record("requests", 150, "2026-10-26T10:00:00")
    daily = ma.aggregate_by_period("requests", "daily")
    assert len(daily) == 2
    assert daily[0]["period"] == "2026-10-25"
    assert daily[0]["sum"] == 300


def test_hourly_aggregation():
    ma = MetricsAggregator()
    ma.record("cpu", 30.0, "2026-10-25T10:00:00")
    ma.record("cpu", 40.0, "2026-10-25T10:30:00")
    ma.record("cpu", 60.0, "2026-10-25T11:00:00")
    hourly = ma.aggregate_by_period("cpu", "hourly")
    assert len(hourly) == 2
    assert hourly[0]["avg"] == 35.0


def test_percentiles():
    ma = MetricsAggregator()
    for i in range(100):
        ma.record("response_time", float(i + 1), f"2026-10-25T{i % 24:02d}:00:00")
    pcts = ma.get_percentiles("response_time")
    assert 49 <= pcts["p50"] <= 51
    assert pcts["p99"] >= 98


def test_compare_periods():
    ma = MetricsAggregator()
    ma.record("revenue", 1000, "2026-10-25T00:00:00")
    ma.record("revenue", 1500, "2026-10-26T00:00:00")
    comp = ma.compare_periods("revenue", "2026-10-25", "2026-10-26")
    assert comp["delta_sum"] == 500
    assert comp["pct_change"] == 50.0


def test_empty_metric():
    ma = MetricsAggregator()
    assert ma.get_totals("nonexistent")["count"] == 0
    assert ma.aggregate_by_period("nonexistent") == []


def test_list_metrics():
    ma = MetricsAggregator()
    ma.record("cpu", 50, "2026-10-25")
    ma.record("memory", 256, "2026-10-25")
    assert ma.list_metrics() == ["cpu", "memory"]
