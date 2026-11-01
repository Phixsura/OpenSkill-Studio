import pytest
from app.services.app_api_developer_api_api_webhook_priority_router import AppAPIDeveloperAPIApiWebhookPriorityRouter

class TestPriorityRouter:
    def test_add_route(self):
        r = AppAPIDeveloperAPIApiWebhookPriorityRouter()
        rt = r.add_route("inst-1", "r1", "payment.completed", "critical", "https://billing.com")
        assert rt.priority == "critical"

    def test_resolve_priority_order(self):
        r = AppAPIDeveloperAPIApiWebhookPriorityRouter()
        r.add_route("inst-1", "r1", "order", "low", "https://a.com")
        r.add_route("inst-1", "r2", "order", "critical", "https://b.com")
        r.add_route("inst-1", "r3", "order", "normal", "https://c.com")
        resolved = r.resolve("inst-1", "order")
        assert resolved[0].priority == "critical"
        assert resolved[-1].priority == "low"

    def test_deliver(self):
        r = AppAPIDeveloperAPIApiWebhookPriorityRouter()
        r.add_route("inst-1", "r1", "push", "high", "https://a.com")
        r.deliver("inst-1", "r1")
        assert r.all_routes("inst-1")[0].delivered_count == 1

    def test_by_priority(self):
        r = AppAPIDeveloperAPIApiWebhookPriorityRouter()
        r.add_route("inst-1", "r1", "a", "critical", "https://a.com")
        r.add_route("inst-1", "r2", "b", "low", "https://b.com")
        assert len(r.by_priority("inst-1", "critical")) == 1

    def test_isolation(self):
        r = AppAPIDeveloperAPIApiWebhookPriorityRouter()
        r.add_route("inst-1", "r1", "push", "high", "https://a.com")
        assert len(r.all_routes("inst-2")) == 0
