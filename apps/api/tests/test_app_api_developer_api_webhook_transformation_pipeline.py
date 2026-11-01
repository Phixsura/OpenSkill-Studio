import pytest
from app.services.app_api_developer_api_webhook_transformation_pipeline import AppAPIDeveloperAPIWebhookTransformationPipeline

class TestTransformPipeline:
    def test_rename(self):
        p = AppAPIDeveloperAPIWebhookTransformationPipeline()
        p.create("inst-1", "p1", [{"step_id": "s1", "operation": "rename_field", "config": {"from": "name", "to": "full_name"}}])
        r = p.execute("inst-1", "p1", {"name": "Alice"})
        assert r == {"full_name": "Alice"}

    def test_remove(self):
        p = AppAPIDeveloperAPIWebhookTransformationPipeline()
        p.create("inst-1", "p1", [{"step_id": "s1", "operation": "remove_field", "config": {"field": "secret"}}])
        r = p.execute("inst-1", "p1", {"name": "Alice", "secret": "xyz"})
        assert "secret" not in r

    def test_add(self):
        p = AppAPIDeveloperAPIWebhookTransformationPipeline()
        p.create("inst-1", "p1", [{"step_id": "s1", "operation": "add_field", "config": {"field": "source", "value": "api"}}])
        r = p.execute("inst-1", "p1", {"name": "Alice"})
        assert r["source"] == "api"

    def test_invalid_operation(self):
        p = AppAPIDeveloperAPIWebhookTransformationPipeline()
        with pytest.raises(ValueError):
            p.create("inst-1", "p1", [{"step_id": "s1", "operation": "hack"}])

    def test_isolation(self):
        p = AppAPIDeveloperAPIWebhookTransformationPipeline()
        p.create("inst-1", "p1", [{"step_id": "s1", "operation": "add_field", "config": {"field": "x", "value": "y"}}])
        assert len(p.list_pipelines("inst-2")) == 0
