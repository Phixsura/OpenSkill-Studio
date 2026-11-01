"""Tests for Consumer API Webhook Transformer service."""
import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_webhook_xform import (
    WebhookTransformer, TransformOp,
)


class TestWebhookTransformer:
    def test_rename(self):
        svc = WebhookTransformer()
        svc.create_pipeline("p1", [TransformOp("rename", {"from": "user_id", "to": "userId"})])
        result = svc.transform("p1", {"user_id": 123, "name": "Alice"})
        assert result["payload"]["userId"] == 123
        assert "user_id" not in result["payload"]

    def test_remove(self):
        svc = WebhookTransformer()
        svc.create_pipeline("p1", [TransformOp("remove", {"field": "secret"})])
        result = svc.transform("p1", {"id": 1, "secret": "hidden"})
        assert "secret" not in result["payload"]

    def test_add(self):
        svc = WebhookTransformer()
        svc.create_pipeline("p1", [TransformOp("add", {"field": "source", "value": "api"})])
        result = svc.transform("p1", {"id": 1})
        assert result["payload"]["source"] == "api"

    def test_flatten(self):
        svc = WebhookTransformer()
        svc.create_pipeline("p1", [TransformOp("flatten", {"field": "address"})])
        result = svc.transform("p1", {"name": "Bob", "address": {"city": "NYC", "zip": "10001"}})
        assert result["payload"]["address_city"] == "NYC"
        assert "address" not in result["payload"]

    def test_wrap(self):
        svc = WebhookTransformer()
        svc.create_pipeline("p1", [TransformOp("wrap", {"key": "event"})])
        result = svc.transform("p1", {"id": 1})
        assert result["payload"]["event"]["id"] == 1

    def test_extract(self):
        svc = WebhookTransformer()
        svc.create_pipeline("p1", [TransformOp("extract", {"field": "data"})])
        result = svc.transform("p1", {"data": {"id": 1, "name": "X"}, "meta": "y"})
        assert result["payload"]["id"] == 1
        assert "meta" not in result["payload"]

    def test_chain(self):
        svc = WebhookTransformer()
        svc.create_pipeline("p1", [
            TransformOp("remove", {"field": "internal"}),
            TransformOp("add", {"field": "version", "value": "2"}),
        ])
        result = svc.transform("p1", {"id": 1, "internal": "x"})
        assert "internal" not in result["payload"]
        assert result["payload"]["version"] == "2"
        assert result["ops_applied"] == 2

    def test_delete_pipeline(self):
        svc = WebhookTransformer()
        svc.create_pipeline("p1", [TransformOp("add", {"field": "x", "value": 1})])
        svc.delete_pipeline("p1")
        assert svc.list_pipelines() == []

    def test_stats(self):
        svc = WebhookTransformer()
        svc.create_pipeline("p1", [TransformOp("add", {"field": "x", "value": 1})])
        svc.transform("p1", {})
        stats = svc.get_stats()
        assert stats["total_transforms"] == 1

    def test_invalid_op(self):
        svc = WebhookTransformer()
        with pytest.raises(ValueError):
            svc.create_pipeline("p1", [TransformOp("encrypt", {})])

    def test_duplicate_pipeline(self):
        svc = WebhookTransformer()
        svc.create_pipeline("p1", [TransformOp("add", {"field": "x", "value": 1})])
        with pytest.raises(ValueError):
            svc.create_pipeline("p1", [])

    def test_isolation(self):
        a, b = WebhookTransformer(), WebhookTransformer()
        a.create_pipeline("p1", [TransformOp("add", {"field": "x", "value": 1})])
        with pytest.raises(ValueError):
            b.transform("p1", {})
