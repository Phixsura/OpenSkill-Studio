"""Tests for Consumer Webhook Template service."""
import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_webhook_template import (
    TemplateManager, WebhookTemplate,
)


class TestTemplateManager:
    def test_create_and_render(self):
        svc = TemplateManager()
        svc.create(WebhookTemplate("t1", "Order Created", "order.created",
                                    {"event": "order.created", "order_id": "{{order.id}}",
                                     "amount": "{{order.amount}}"}))
        result = svc.render("t1", {"order": {"id": "ord-123", "amount": "99.99"}})
        assert result["body"]["order_id"] == "ord-123"
        assert result["body"]["amount"] == "99.99"

    def test_extract_placeholders(self):
        svc = TemplateManager()
        result = svc.create(WebhookTemplate("t1", "Test", "test",
                                             {"a": "{{user.name}}", "b": "{{user.email}}"}))
        assert "user.name" in result["placeholders"]
        assert "user.email" in result["placeholders"]

    def test_header_substitution(self):
        svc = TemplateManager()
        svc.create(WebhookTemplate("t1", "T", "test", {"msg": "hi"},
                                    headers_template={"X-Consumer": "{{consumer_id}}"}))
        result = svc.render("t1", {"consumer_id": "c-123"})
        assert result["headers"]["X-Consumer"] == "c-123"

    def test_missing_variable_preserved(self):
        svc = TemplateManager()
        svc.create(WebhookTemplate("t1", "T", "test", {"val": "{{missing}}"}))
        result = svc.render("t1", {})
        assert result["body"]["val"] == "{{missing}}"

    def test_preview(self):
        svc = TemplateManager()
        svc.create(WebhookTemplate("t1", "Order", "order.created",
                                    {"id": "{{order_id}}"}))
        preview = svc.preview("t1")
        assert preview["name"] == "Order"
        assert "order_id" in preview["placeholders"]

    def test_list_by_event(self):
        svc = TemplateManager()
        svc.create(WebhookTemplate("t1", "A", "order.created", {"x": "1"}))
        svc.create(WebhookTemplate("t2", "B", "user.created", {"x": "2"}))
        results = svc.list_templates(event_type="order.created")
        assert len(results) == 1

    def test_delete(self):
        svc = TemplateManager()
        svc.create(WebhookTemplate("t1", "T", "test", {"x": "1"}))
        assert svc.delete("t1")["deleted"] is True
        assert svc.list_templates() == []

    def test_clone(self):
        svc = TemplateManager()
        svc.create(WebhookTemplate("t1", "Original", "test", {"msg": "{{text}}"}))
        result = svc.clone("t1", "t2", "Clone")
        assert result["cloned_from"] == "t1"
        rendered = svc.render("t2", {"text": "hello"})
        assert rendered["body"]["msg"] == "hello"

    def test_duplicate_rejected(self):
        svc = TemplateManager()
        svc.create(WebhookTemplate("t1", "T", "test", {"x": "1"}))
        with pytest.raises(ValueError):
            svc.create(WebhookTemplate("t1", "T2", "test", {"y": "2"}))

    def test_empty_body_rejected(self):
        svc = TemplateManager()
        with pytest.raises(ValueError):
            svc.create(WebhookTemplate("t1", "T", "test", {}))

    def test_isolation(self):
        a, b = TemplateManager(), TemplateManager()
        a.create(WebhookTemplate("t1", "T", "test", {"x": "1"}))
        assert b.list_templates() == []
