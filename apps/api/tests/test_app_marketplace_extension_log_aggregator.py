from app.services.app_marketplace_extension_log_aggregator import ExtLogAggregatorService

def test_log_and_query():
    svc = ExtLogAggregatorService()
    svc.log("ext-1", "info", "Server started")
    svc.log("ext-1", "error", "Connection failed")
    svc.log("ext-2", "info", "Other extension")
    results = svc.query(extension_id="ext-1")
    assert len(results) == 2

def test_min_level():
    svc = ExtLogAggregatorService()
    svc.log("ext-1", "debug", "Debug msg")
    svc.log("ext-1", "warn", "Warning")
    svc.log("ext-1", "error", "Error!")
    results = svc.query(extension_id="ext-1", min_level="warn")
    assert len(results) == 2

def test_search():
    svc = ExtLogAggregatorService()
    svc.log("ext-1", "info", "User login successful")
    svc.log("ext-1", "info", "Data processed")
    results = svc.query(search="login")
    assert len(results) == 1

def test_counts():
    svc = ExtLogAggregatorService()
    svc.log("ext-1", "info", "a")
    svc.log("ext-1", "error", "b")
    svc.log("ext-1", "error", "c")
    counts = svc.get_counts("ext-1")
    assert counts["error"] == 2
    assert counts["info"] == 1
