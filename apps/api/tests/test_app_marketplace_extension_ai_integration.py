from app.services.app_marketplace_extension_ai_integration import ExtensionAIIntegrationService
import pytest


def test_list_models():
    svc = ExtensionAIIntegrationService()
    models = svc.list_models()
    assert len(models) >= 4
    assert any(m.name == "Claude Sonnet 5" for m in models)


def test_record_usage():
    svc = ExtensionAIIntegrationService()
    usage = svc.record_usage("ext-1", "claude-sonnet-5", 1000, 500)
    assert usage.requests == 1
    assert usage.input_tokens == 1000
    assert usage.total_cost_cents > 0


def test_estimate_cost():
    svc = ExtensionAIIntegrationService()
    est = svc.estimate_cost("gpt-4o-mini", 10000, 5000)
    assert est["cost_cents"] > 0
    assert est["model"] == "GPT-4o Mini"


def test_total_cost():
    svc = ExtensionAIIntegrationService()
    svc.record_usage("ext-1", "claude-sonnet-5", 5000, 2000)
    svc.record_usage("ext-1", "gpt-4o-mini", 10000, 5000)
    total = svc.get_total_cost("ext-1")
    assert total > 0


def test_unknown_model():
    svc = ExtensionAIIntegrationService()
    with pytest.raises(ValueError):
        svc.record_usage("ext-1", "unknown-model", 100, 50)


def test_cached_tracking():
    svc = ExtensionAIIntegrationService()
    svc.record_usage("ext-1", "claude-haiku-4.5", 500, 200, cached=True)
    usage = svc.get_usage("ext-1")
    assert usage[0].cached_responses == 1
