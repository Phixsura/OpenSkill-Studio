from app.services.app_webhook_test_console import prepare_test_delivery

def test_prepare():
    d = prepare_test_delivery(event_type="submission.completed", webhook_url="https://x.com/hook", webhook_secret="secret123")
    assert d["url"] == "https://x.com/hook"
    assert d["method"] == "POST"
    assert "X-OpenSkill-Signature" in d["headers"]
    assert d["body"]["test"] is True

def test_headers():
    d = prepare_test_delivery(event_type="app.installed", webhook_url="u", webhook_secret="s")
    assert d["headers"]["Content-Type"] == "application/json"
    assert d["headers"]["X-OpenSkill-Event"] == "app.installed"

def test_payload_size():
    d = prepare_test_delivery(event_type="test", webhook_url="u", webhook_secret="s")
    assert d["payload_size"] > 0
