from app.services.app_marketplace_log_aggregator import LogAggregator, AggregatedLog


def test_ingest_and_search():
    la = LogAggregator()
    la.ingest(AggregatedLog("ext-1", "i1", "info", "Server started on port 8080"))
    la.ingest(AggregatedLog("ext-1", "i1", "error", "Connection refused to db"))
    la.ingest(AggregatedLog("ext-2", "i2", "info", "Ready"))
    results = la.search("connection", extension_id="ext-1")
    assert len(results) == 1
    assert "refused" in results[0].message


def test_search_by_level():
    la = LogAggregator()
    la.ingest(AggregatedLog("ext-3", "i1", "info", "ok"))
    la.ingest(AggregatedLog("ext-3", "i1", "error", "fail"))
    errors = la.search("", extension_id="ext-3", level="error")
    assert len(errors) == 1


def test_volume():
    la = LogAggregator()
    for _ in range(5):
        la.ingest(AggregatedLog("ext-4", "i1", "info", "ok"))
    for _ in range(3):
        la.ingest(AggregatedLog("ext-4", "i1", "error", "fail"))
    vol = la.get_volume("ext-4")
    assert vol["total"] == 8
    assert vol["by_level"]["info"] == 5
    assert vol["by_level"]["error"] == 3


def test_frequent_patterns():
    la = LogAggregator()
    for _ in range(10):
        la.ingest(AggregatedLog("ext-5", "i1", "warn", "Slow query detected in user_lookup"))
    for _ in range(3):
        la.ingest(AggregatedLog("ext-5", "i1", "info", "Cache hit"))
    patterns = la.get_frequent_patterns("ext-5")
    assert patterns[0]["count"] == 10


def test_error_summary():
    la = LogAggregator()
    la.ingest(AggregatedLog("ext-6", "i1", "error", "Timeout"))
    la.ingest(AggregatedLog("ext-6", "i2", "error", "Timeout"))
    la.ingest(AggregatedLog("ext-6", "i1", "error", "OOM killed"))
    summary = la.get_error_summary("ext-6")
    assert summary["total_errors"] == 3
    assert summary["unique_errors"] == 2


def test_instance_distribution():
    la = LogAggregator()
    la.ingest(AggregatedLog("ext-7", "i1", "info", "a"))
    la.ingest(AggregatedLog("ext-7", "i1", "info", "b"))
    la.ingest(AggregatedLog("ext-7", "i2", "info", "c"))
    dist = la.get_instance_distribution("ext-7")
    assert dist["i1"] == 2
    assert dist["i2"] == 1
