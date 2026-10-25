from app.services.app_marketplace_log_collector import LogCollector, LogLevel


def test_log_and_query():
    lc = LogCollector()
    lc.info("ext-1", "Server started", port=8080)
    lc.debug("ext-1", "Loading config")
    lc.error("ext-1", "Connection failed", host="db.local")
    all_logs = lc.query("ext-1")
    assert len(all_logs) == 3


def test_level_filtering():
    lc = LogCollector()
    lc.debug("ext-2", "debug msg")
    lc.info("ext-2", "info msg")
    lc.error("ext-2", "error msg")
    errors = lc.query("ext-2", min_level=LogLevel.ERROR)
    assert len(errors) == 1
    assert errors[0].message == "error msg"


def test_search():
    lc = LogCollector()
    lc.info("ext-3", "Processing batch 1")
    lc.info("ext-3", "Processing batch 2")
    lc.info("ext-3", "Upload complete")
    results = lc.query("ext-3", search="batch")
    assert len(results) == 2


def test_trace_id():
    lc = LogCollector()
    lc.info("ext-4", "Start", trace_id="tx-001")
    lc.info("ext-4", "Step 2", trace_id="tx-001")
    lc.info("ext-4", "Other", trace_id="tx-002")
    traced = lc.query("ext-4", trace_id="tx-001")
    assert len(traced) == 2


def test_retention():
    lc = LogCollector(max_entries_per_ext=5)
    for i in range(10):
        lc.info("ext-5", f"Log {i}")
    assert len(lc.query("ext-5")) == 5


def test_error_summary():
    lc = LogCollector()
    lc.info("ext-6", "ok")
    lc.warning("ext-6", "slow query")
    lc.error("ext-6", "timeout")
    lc.critical("ext-6", "crash")
    summary = lc.get_error_summary("ext-6")
    assert summary["total_entries"] == 4
    assert summary["by_level"]["ERROR"] == 1
    assert summary["by_level"]["CRITICAL"] == 1
    assert len(summary["recent_errors"]) == 2


def test_clear():
    lc = LogCollector()
    lc.info("ext-7", "a")
    lc.info("ext-7", "b")
    cleared = lc.clear("ext-7")
    assert cleared == 2
    assert lc.query("ext-7") == []
