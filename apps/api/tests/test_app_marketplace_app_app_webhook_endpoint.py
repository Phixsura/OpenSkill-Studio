from app.services.app_marketplace_app_app_webhook_endpoint import create_webhook_endpoint, build_endpoint_list

def test_create():
    r = create_webhook_endpoint(url="https://example.com/webhook",
                                  events=["app.installed", "app.updated"],
                                  description="My webhook")
    assert r["id"].startswith("we_")
    assert r["secret"].startswith("whsec_")
    assert len(r["events"]) == 2

def test_http_rejected():
    r = create_webhook_endpoint(url="http://insecure.com/hook", events=[])
    assert "error" in r

def test_list():
    endpoints = [
        {"active": True, "events": ["a", "b"]},
        {"active": False, "events": ["c"]},
    ]
    r = build_endpoint_list(endpoints=endpoints)
    assert r["active"] == 1
    assert r["total_event_subscriptions"] == 3
