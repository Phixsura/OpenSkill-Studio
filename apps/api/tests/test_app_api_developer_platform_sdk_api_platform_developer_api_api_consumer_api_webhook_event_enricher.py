from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_webhook_event_enricher import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiWebhookEventEnricher, EnrichmentConfig, EnrichmentRule,
)

class TestWebhookEventEnricher:
    def test_static_enrichment(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiWebhookEventEnricher()
        svc.configure("inst-1", EnrichmentConfig(consumer_id="c1", rules=[EnrichmentRule(rule_id="r1", field_name="env", source="static", value="production")]))
        result = svc.enrich("inst-1", "c1", {"event": "test"})
        assert result["env"] == "production" and result["event"] == "test"

    def test_lookup_enrichment(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiWebhookEventEnricher()
        svc.set_lookup("inst-1", "org_name", "Acme Corp")
        svc.configure("inst-1", EnrichmentConfig(consumer_id="c1", rules=[EnrichmentRule(rule_id="r1", field_name="organization", source="lookup", lookup_key="org_name")]))
        result = svc.enrich("inst-1", "c1", {})
        assert result["organization"] == "Acme Corp"

    def test_disabled_config(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiWebhookEventEnricher()
        svc.configure("inst-1", EnrichmentConfig(consumer_id="c1", enabled=False, rules=[EnrichmentRule(rule_id="r1", field_name="x", source="static", value="y")]))
        result = svc.enrich("inst-1", "c1", {"data": 1})
        assert "x" not in result

    def test_no_config_passthrough(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiWebhookEventEnricher()
        result = svc.enrich("inst-1", "c1", {"original": True})
        assert result == {"original": True}

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiWebhookEventEnricher()
        svc.configure("inst-1", EnrichmentConfig(consumer_id="c1"))
        assert len(svc.list_configs("inst-2")) == 0
