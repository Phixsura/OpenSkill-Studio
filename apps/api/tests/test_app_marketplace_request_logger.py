from app.services.app_marketplace_request_logger import RequestLogger, RequestLog


def test_log_and_query():
    rl = RequestLogger()
    rl.log(RequestLog("r1", "GET", "/api/ext", 200, 45.0, "ext-1"))
    rl.log(RequestLog("r2", "POST", "/api/ext", 201, 120.0, "ext-1"))
    results = rl.query(extension_id="ext-1")
    assert len(results) == 2


def test_filter_by_method():
    rl = RequestLogger()
    rl.log(RequestLog("r1", "GET", "/a", 200, 10.0, "ext-2"))
    rl.log(RequestLog("r2", "POST", "/b", 201, 20.0, "ext-2"))
    gets = rl.query(extension_id="ext-2", method="GET")
    assert len(gets) == 1


def test_error_requests():
    rl = RequestLogger()
    rl.log(RequestLog("r1", "GET", "/ok", 200, 10.0, "ext-3"))
    rl.log(RequestLog("r2", "GET", "/bad", 500, 50.0, "ext-3", error="Internal error"))
    rl.log(RequestLog("r3", "GET", "/notfound", 404, 5.0, "ext-3"))
    errors = rl.get_error_requests("ext-3")
    assert len(errors) == 2


def test_slow_requests():
    rl = RequestLogger()
    rl.log(RequestLog("r1", "GET", "/fast", 200, 50.0, "ext-4"))
    rl.log(RequestLog("r2", "GET", "/slow", 200, 2500.0, "ext-4"))
    slow = rl.get_slow_requests("ext-4", threshold_ms=1000)
    assert len(slow) == 1
    assert slow[0].path == "/slow"


def test_summary():
    rl = RequestLogger()
    rl.log(RequestLog("r1", "GET", "/", 200, 30.0, "ext-5"))
    rl.log(RequestLog("r2", "GET", "/", 200, 50.0, "ext-5"))
    rl.log(RequestLog("r3", "GET", "/", 500, 100.0, "ext-5"))
    summary = rl.get_summary("ext-5")
    assert summary["total_requests"] == 3
    assert summary["error_count"] == 1
    assert summary["status_2xx"] == 2
    assert summary["status_5xx"] == 1
    assert summary["avg_duration_ms"] == 60.0


def test_retention():
    rl = RequestLogger(max_logs=5)
    for i in range(10):
        rl.log(RequestLog(f"r{i}", "GET", "/", 200, 10.0, "ext-6"))
    assert len(rl.query()) == 5
