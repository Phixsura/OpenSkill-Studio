from app.services.app_marketplace_app_app_app_app_app_app_app_err_correlate import correlate_errors

def test_correlate():
    r = correlate_errors([
        {"service": "api", "error": "timeout", "trace_id": "t1", "timestamp": 1},
        {"service": "db", "error": "conn_refused", "trace_id": "t1", "timestamp": 2},
        {"service": "api", "error": "500", "trace_id": "t2", "timestamp": 3},
    ])
    assert r["correlated_cascades"] == 1
    assert r["cascades"][0]["root_service"] == "api"
    assert r["unique_traces"] == 2
