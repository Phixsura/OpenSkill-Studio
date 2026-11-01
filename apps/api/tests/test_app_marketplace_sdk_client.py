from app.services.app_marketplace_sdk_client import OpenSkillSDK, SDKConfig


def _make_sdk() -> OpenSkillSDK:
    return OpenSkillSDK(SDKConfig(api_key="osk_test_key_1234567890"))


def test_get_extension():
    sdk = _make_sdk()
    result = sdk.get_extension("ext-1")
    assert result["ok"] is True
    assert "/extensions/ext-1" in result["endpoint"]


def test_publish_version():
    sdk = _make_sdk()
    result = sdk.publish_version("ext-1", "2.0.0", "Major update")
    assert result["method"] == "POST"
    assert "/versions" in result["endpoint"]


def test_webhook_crud():
    sdk = _make_sdk()
    sdk.create_webhook("https://hook.test/a", ["install", "review"])
    sdk.list_webhooks()
    sdk.delete_webhook("wh-123")
    log = sdk.get_call_log()
    assert len(log) == 3
    assert log[0]["method"] == "POST"
    assert log[2]["method"] == "DELETE"


def test_config_management():
    sdk = _make_sdk()
    sdk.set_config("ext-1", "org-1", {"theme": "dark"})
    result = sdk.get_config("ext-1", "org-1")
    assert result["ok"] is True


def test_events_and_analytics():
    sdk = _make_sdk()
    sdk.emit_event("user.action", {"action": "click"})
    sdk.get_analytics("ext-1", "30d")
    log = sdk.get_call_log()
    assert any("/events" in c["endpoint"] for c in log)
    assert any("/analytics" in c["endpoint"] for c in log)


def test_health_report():
    sdk = _make_sdk()
    result = sdk.report_health("ext-1", "healthy", 42.5)
    assert result["method"] == "POST"
    assert "/health" in result["endpoint"]


def test_api_key_prefix_masked():
    sdk = _make_sdk()
    sdk.get_extension("ext-1")
    log = sdk.get_call_log()
    assert log[0]["api_key_prefix"] == "osk_test..."
