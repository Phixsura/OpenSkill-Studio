from app.services.app_marketplace_extension_webhook_transform import (
    WebhookTransformService,
)


def test_map_fields():
    svc = WebhookTransformService()
    p = svc.create_pipeline("Rename", "push", [
        {"op": "map", "config": {"fields": {"user_name": "author", "repo": "repository"}}},
    ])
    result = svc.transform(p.pipeline_id, {"user_name": "alice", "repo": "my-app", "sha": "abc"})
    assert result["author"] == "alice"
    assert result["repository"] == "my-app"
    assert result["sha"] == "abc"  # unmapped kept


def test_filter_include():
    svc = WebhookTransformService()
    p = svc.create_pipeline("Filter", "push", [
        {"op": "filter", "config": {"include": ["ref", "sha"]}},
    ])
    result = svc.transform(p.pipeline_id, {"ref": "main", "sha": "abc", "extra": "data"})
    assert "ref" in result
    assert "extra" not in result


def test_filter_exclude():
    svc = WebhookTransformService()
    p = svc.create_pipeline("Filter", "push", [
        {"op": "filter", "config": {"exclude": ["secret", "internal"]}},
    ])
    result = svc.transform(p.pipeline_id, {"name": "test", "secret": "key", "internal": "x"})
    assert "name" in result
    assert "secret" not in result


def test_enrich():
    svc = WebhookTransformService()
    p = svc.create_pipeline("Enrich", "deploy", [
        {"op": "enrich", "config": {"fields": {"source": "marketplace", "version": "2.0"}}},
    ])
    result = svc.transform(p.pipeline_id, {"status": "ok"})
    assert result["source"] == "marketplace"
    assert result["status"] == "ok"


def test_flatten():
    svc = WebhookTransformService()
    p = svc.create_pipeline("Flatten", "event", [
        {"op": "flatten"},
    ])
    result = svc.transform(p.pipeline_id, {"user": {"name": "alice", "id": 1}, "action": "push"})
    assert result["user_name"] == "alice"
    assert result["user_id"] == 1
    assert result["action"] == "push"


def test_wrap():
    svc = WebhookTransformService()
    p = svc.create_pipeline("Wrap", "event", [
        {"op": "wrap", "config": {"key": "payload"}},
    ])
    result = svc.transform(p.pipeline_id, {"a": 1})
    assert result == {"payload": {"a": 1}}


def test_pipeline_chain():
    svc = WebhookTransformService()
    p = svc.create_pipeline("Chain", "push", [
        {"op": "filter", "config": {"include": ["name", "status"]}},
        {"op": "enrich", "config": {"fields": {"processed": True}}},
        {"op": "wrap", "config": {"key": "data"}},
    ])
    result = svc.transform(p.pipeline_id, {"name": "test", "status": "ok", "extra": "x"})
    assert result == {"data": {"name": "test", "status": "ok", "processed": True}}


def test_execution_count():
    svc = WebhookTransformService()
    p = svc.create_pipeline("P", "e", [{"op": "wrap", "config": {"key": "d"}}])
    svc.transform(p.pipeline_id, {})
    svc.transform(p.pipeline_id, {})
    assert p.execution_count == 2
