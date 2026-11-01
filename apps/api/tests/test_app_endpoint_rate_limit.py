from app.services.app_endpoint_rate_limit import record_endpoint_call, get_endpoint_usage, check_endpoint_limit

def test_record():
    record_endpoint_call("erl1", "/api/v1/cohorts")
    usage = get_endpoint_usage("erl1")
    assert usage.get("/api/v1/cohorts", 0) >= 1

def test_limit_ok():
    assert check_endpoint_limit("erl2", "/api/v1/test") is True

def test_limit_exceeded():
    app = "erl3"
    for _ in range(101):
        record_endpoint_call(app, "/api/v1/heavy")
    assert check_endpoint_limit(app, "/api/v1/heavy", limit=100) is False
