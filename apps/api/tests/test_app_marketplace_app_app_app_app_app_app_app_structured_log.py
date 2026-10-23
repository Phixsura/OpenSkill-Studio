from app.services.app_marketplace_app_app_app_app_app_app_app_structured_log import parse_logs, filter_logs

def test_parse():
    lines = [
        '{"level": "info", "service": "api", "message": "Request handled"}',
        '{"level": "error", "service": "api", "message": "DB timeout"}',
        '{"level": "info", "service": "worker", "message": "Job done"}',
        'not json',
    ]
    r = parse_logs(lines)
    assert r["total"] == 4
    assert r["parsed"] == 3
    assert r["parse_errors"] == 1
    assert r["error_count"] == 1
    assert r["has_errors"]

def test_filter():
    logs = [
        {"level": "info", "service": "api", "message": "ok"},
        {"level": "error", "service": "api", "message": "fail"},
        {"level": "info", "service": "worker", "message": "done"},
    ]
    assert len(filter_logs(logs, level="error")) == 1
    assert len(filter_logs(logs, service="worker")) == 1
    assert len(filter_logs(logs, search="fail")) == 1
