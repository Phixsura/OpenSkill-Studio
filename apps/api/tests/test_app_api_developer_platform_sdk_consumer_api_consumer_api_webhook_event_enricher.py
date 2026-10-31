import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_consumer_api_webhook_event_enricher import (
    AppAPIDeveloperPlatformSDKConsumerApiConsumerApiWebhookEventEnricher, EnrichmentConfig, EnrichmentRule,
)

class TestWebhookEventEnricher:
    def test_static_enrichment(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerApiWebhookEventEnricher()
        svc.set_config("inst-1", "c1", EnrichmentConfig(config_id="e1", webhook_id="w1", rules=[
            EnrichmentRule(rule_id="r1", source_type="static", target_field="source", value="my-api"),
        ]))
        result = svc.enrich("inst-1", "c1", "w1", {"event": "created"})
        assert result.payload["source"] == "my-api" and result.rules_applied == 1

    def test_computed_payload_size(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerApiWebhookEventEnricher()
        svc.set_config("inst-1", "c1", EnrichmentConfig(config_id="e1", webhook_id="w1", rules=[
            EnrichmentRule(rule_id="r1", source_type="computed", target_field="size", value="payload_size"),
        ]))
        result = svc.enrich("inst-1", "c1", "w1", {"data": "test"})
        assert result.payload["size"] > 0

    def test_computed_field_count(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerApiWebhookEventEnricher()
        svc.set_config("inst-1", "c1", EnrichmentConfig(config_id="e1", webhook_id="w1", rules=[
            EnrichmentRule(rule_id="r1", source_type="computed", target_field="fields", value="field_count"),
        ]))
        result = svc.enrich("inst-1", "c1", "w1", {"a": 1, "b": 2, "c": 3})
        assert result.payload["fields"] == 3

    def test_disabled_passthrough(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerApiWebhookEventEnricher()
        svc.set_config("inst-1", "c1", EnrichmentConfig(config_id="e1", webhook_id="w1", enabled=False, rules=[
            EnrichmentRule(rule_id="r1", source_type="static", target_field="x", value="y"),
        ]))
        result = svc.enrich("inst-1", "c1", "w1", {"data": 1})
        assert "x" not in result.payload

    def test_invalid_source_type(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerApiWebhookEventEnricher()
        with pytest.raises(ValueError, match="Invalid source_type"):
            svc.set_config("inst-1", "c1", EnrichmentConfig(config_id="e1", webhook_id="w1", rules=[
                EnrichmentRule(rule_id="r1", source_type="magic", target_field="x"),
            ]))

    def test_no_config_passthrough(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerApiWebhookEventEnricher()
        result = svc.enrich("inst-1", "c1", "w1", {"data": 1})
        assert result.rules_applied == 0

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerApiWebhookEventEnricher()
        svc.set_config("inst-1", "c1", EnrichmentConfig(config_id="e1", webhook_id="w1", rules=[EnrichmentRule(rule_id="r1", source_type="static", target_field="x", value="y")]))
        assert svc.get_config("inst-2", "c1", "w1") is None
