from app.services.app_marketplace_app_app_app_app_app_app_app_webhook_filter import create_filter, apply_filter

def test_include():
    f = create_filter("prod_only", [
        {"name": "env_check", "field": "environment", "operator": "eq", "value": "production", "action": "include"}
    ])
    r = apply_filter(f, {"environment": "production", "event": "deploy"})
    assert r["delivered"]

def test_exclude():
    f = create_filter("no_test", [
        {"name": "skip_test", "field": "environment", "operator": "eq", "value": "test", "action": "exclude"}
    ])
    r = apply_filter(f, {"environment": "test"})
    assert not r["delivered"]

def test_regex():
    f = create_filter("error_only", [
        {"name": "err", "field": "message", "operator": "regex", "value": "error|fail", "action": "include"}
    ])
    r = apply_filter(f, {"message": "deployment failed"})
    assert r["delivered"]
