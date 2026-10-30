import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_api_webhook_transform_pipeline import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiWebhookTransformPipeline, Pipeline, TransformStep,
)

class TestConsumerApiWebhookTransformPipeline:
    def test_filter_step(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiWebhookTransformPipeline()
        svc.create_pipeline("inst-1", "c1", Pipeline(pipeline_id="p1", webhook_id="w1", steps=[TransformStep(step_id="s1", step_type="filter", config={"fields": "id,name"})]))
        result = svc.execute("inst-1", "c1", "p1", {"id": "1", "name": "A", "secret": "x"})
        assert "secret" not in result.output_payload and result.output_payload["id"] == "1"

    def test_map_step(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiWebhookTransformPipeline()
        svc.create_pipeline("inst-1", "c1", Pipeline(pipeline_id="p1", webhook_id="w1", steps=[TransformStep(step_id="s1", step_type="map", config={"user_id": "id"})]))
        result = svc.execute("inst-1", "c1", "p1", {"user_id": "123"})
        assert result.output_payload["id"] == "123" and "user_id" not in result.output_payload

    def test_redact_step(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiWebhookTransformPipeline()
        svc.create_pipeline("inst-1", "c1", Pipeline(pipeline_id="p1", webhook_id="w1", steps=[TransformStep(step_id="s1", step_type="redact", config={"fields": "email,ssn"})]))
        result = svc.execute("inst-1", "c1", "p1", {"name": "Alice", "email": "a@b.com", "ssn": "123"})
        assert result.output_payload["email"] == "***" and result.output_payload["name"] == "Alice"

    def test_chained_steps(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiWebhookTransformPipeline()
        svc.create_pipeline("inst-1", "c1", Pipeline(pipeline_id="p1", webhook_id="w1", steps=[
            TransformStep(step_id="s1", step_type="enrich", config={"source": "api"}, order=1),
            TransformStep(step_id="s2", step_type="redact", config={"fields": "secret"}, order=2),
        ]))
        result = svc.execute("inst-1", "c1", "p1", {"data": "x", "secret": "s"})
        assert result.output_payload["source"] == "api" and result.output_payload["secret"] == "***"
        assert result.steps_executed == 2

    def test_disabled_step(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiWebhookTransformPipeline()
        svc.create_pipeline("inst-1", "c1", Pipeline(pipeline_id="p1", webhook_id="w1", steps=[TransformStep(step_id="s1", step_type="filter", config={"fields": "id"}, enabled=False)]))
        result = svc.execute("inst-1", "c1", "p1", {"id": "1", "extra": "x"})
        assert "extra" in result.output_payload and result.steps_skipped == 1

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiWebhookTransformPipeline()
        svc.create_pipeline("inst-1", "c1", Pipeline(pipeline_id="p1", webhook_id="w1", steps=[]))
        assert len(svc.list_pipelines("inst-2", "c1")) == 0
