from app.services.app_api_developer_platform_sdk_developer_api_webhook_event_enrichment import AppAPIDeveloperPlatformSDKDeveloperApiWebhookEventEnrichment

class TestWebhookEventEnrichment:
    def test_static_enrichment(self):
        e = AppAPIDeveloperPlatformSDKDeveloperApiWebhookEventEnrichment()
        e.add_rule("inst-1", "https://a.com", "r1", "source", "static", "platform")
        result = e.enrich("inst-1", "https://a.com", {"data": "test"})
        assert result["source"] == "platform"
        assert result["data"] == "test"

    def test_consumer_enrichment(self):
        e = AppAPIDeveloperPlatformSDKDeveloperApiWebhookEventEnrichment()
        e.add_rule("inst-1", "https://a.com", "r1", "consumer", "consumer")
        result = e.enrich("inst-1", "https://a.com", {}, consumer_id="acme")
        assert result["consumer"] == "acme"

    def test_request_id(self):
        e = AppAPIDeveloperPlatformSDKDeveloperApiWebhookEventEnrichment()
        e.add_rule("inst-1", "https://a.com", "r1", "req_id", "request_id")
        result = e.enrich("inst-1", "https://a.com", {}, request_id="req-123")
        assert result["req_id"] == "req-123"

    def test_applied_count(self):
        e = AppAPIDeveloperPlatformSDKDeveloperApiWebhookEventEnrichment()
        e.add_rule("inst-1", "https://a.com", "r1", "x", "static", "y")
        e.enrich("inst-1", "https://a.com", {})
        e.enrich("inst-1", "https://a.com", {})
        assert e.rules_for("inst-1", "https://a.com")[0].applied_count == 2

    def test_no_rules(self):
        e = AppAPIDeveloperPlatformSDKDeveloperApiWebhookEventEnrichment()
        result = e.enrich("inst-1", "https://unknown.com", {"data": 1})
        assert result == {"data": 1}
