from app.services.app_marketplace_extension_sandbox_webhook_interceptor import (
    SandboxWebhookInterceptorService,
)


def test_intercept_capture():
    svc = SandboxWebhookInterceptorService()
    cap = svc.intercept("sb-1", "outbound", "https://api.example.com/hook",
                        "POST", {"Content-Type": "application/json"},
                        '{"event":"deploy"}', 200)
    assert cap.direction == "outbound"
    assert not cap.paused


def test_rule_pause():
    svc = SandboxWebhookInterceptorService()
    svc.add_rule("sb-1", "example.com", pause=True)
    cap = svc.intercept("sb-1", "outbound", "https://api.example.com/hook",
                        "POST", {}, '{}')
    assert cap.paused is True


def test_resume_with_modification():
    svc = SandboxWebhookInterceptorService()
    svc.add_rule("sb-1", "example.com", pause=True)
    cap = svc.intercept("sb-1", "outbound", "https://api.example.com",
                        "POST", {}, '{"original": true}')
    assert svc.resume("sb-1", cap.intercept_id, '{"modified": true}') is True
    assert cap.modified is True
    assert cap.body == '{"modified": true}'


def test_direction_filter():
    svc = SandboxWebhookInterceptorService()
    svc.intercept("sb-1", "inbound", "https://a.com", "POST", {}, "{}")
    svc.intercept("sb-1", "outbound", "https://b.com", "POST", {}, "{}")
    inbound = svc.get_captures("sb-1", direction="inbound")
    assert len(inbound) == 1


def test_get_paused():
    svc = SandboxWebhookInterceptorService()
    svc.add_rule("sb-1", "pause.com", pause=True)
    svc.intercept("sb-1", "outbound", "https://pause.com/hook", "POST", {}, "{}")
    svc.intercept("sb-1", "outbound", "https://other.com/hook", "POST", {}, "{}")
    paused = svc.get_paused("sb-1")
    assert len(paused) == 1


def test_clear():
    svc = SandboxWebhookInterceptorService()
    svc.intercept("sb-1", "outbound", "https://a.com", "POST", {}, "{}")
    svc.intercept("sb-1", "outbound", "https://b.com", "POST", {}, "{}")
    assert svc.clear("sb-1") == 2
    assert len(svc.get_captures("sb-1")) == 0


def test_remove_rule():
    svc = SandboxWebhookInterceptorService()
    rule = svc.add_rule("sb-1", "example.com")
    assert svc.remove_rule("sb-1", rule.rule_id) is True


def test_rule_direction_filter():
    svc = SandboxWebhookInterceptorService()
    svc.add_rule("sb-1", "example.com", direction="inbound", pause=True)
    # Outbound should NOT be paused
    cap = svc.intercept("sb-1", "outbound", "https://example.com", "POST", {}, "{}")
    assert cap.paused is False
    # Inbound should be paused
    cap2 = svc.intercept("sb-1", "inbound", "https://example.com", "POST", {}, "{}")
    assert cap2.paused is True
