import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_webhook_transform_pipeline import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiWebhookTransformPipeline, TransformStep,
)

class TestWebhookTransformPipeline:
    def test_add_and_remove(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiWebhookTransformPipeline()
        steps = [
            TransformStep(step_id="s1", transform_type="add_field", config={"field": "version", "value": "2.0"}),
            TransformStep(step_id="s2", transform_type="remove_field", config={"field": "internal_id"}),
        ]
        svc.create_pipeline("inst-1", "p1", "c1", steps)
        result = svc.execute("inst-1", "p1", {"id": "1", "internal_id": "secret"})
        assert result["version"] == "2.0"
        assert "internal_id" not in result

    def test_rename(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiWebhookTransformPipeline()
        svc.create_pipeline("inst-1", "p1", "c1", [TransformStep(step_id="s1", transform_type="rename_field", config={"from": "name", "to": "full_name"})])
        result = svc.execute("inst-1", "p1", {"name": "Alice"})
        assert result["full_name"] == "Alice" and "name" not in result

    def test_wrap(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiWebhookTransformPipeline()
        svc.create_pipeline("inst-1", "p1", "c1", [TransformStep(step_id="s1", transform_type="wrap", config={"key": "payload"})])
        result = svc.execute("inst-1", "p1", {"id": "1"})
        assert result["payload"]["id"] == "1"

    def test_execution_count(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiWebhookTransformPipeline()
        svc.create_pipeline("inst-1", "p1", "c1", [TransformStep(step_id="s1", transform_type="add_field", config={"field": "x", "value": "y"})])
        svc.execute("inst-1", "p1", {})
        svc.execute("inst-1", "p1", {})
        assert svc._get("inst-1", "p1").executions == 2

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiWebhookTransformPipeline()
        svc.create_pipeline("inst-1", "p1", "c1", [TransformStep(step_id="s1", transform_type="add_field", config={"field": "x", "value": "y"})])
        assert len(svc.list_pipelines("inst-2")) == 0
