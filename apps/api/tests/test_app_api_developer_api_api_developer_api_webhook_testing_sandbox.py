import pytest
from app.services.app_api_developer_api_api_developer_api_webhook_testing_sandbox import AppAPIDeveloperAPIApiDeveloperApiWebhookTestingSandbox

class TestWebhookTestingSandbox:
    def test_send_success(self):
        s = AppAPIDeveloperAPIApiDeveloperApiWebhookTestingSandbox()
        t = s.send_test("inst-1", "t1", "https://a.com/hook", "push", '{"ref":"main"}', 200, duration_ms=50)
        assert t.success is True

    def test_send_failure(self):
        s = AppAPIDeveloperAPIApiDeveloperApiWebhookTestingSandbox()
        t = s.send_test("inst-1", "t1", "https://a.com/hook", "push", "{}", 500, duration_ms=100)
        assert t.success is False

    def test_https_required(self):
        s = AppAPIDeveloperAPIApiDeveloperApiWebhookTestingSandbox()
        with pytest.raises(ValueError):
            s.send_test("inst-1", "t1", "http://bad.com", "push", "{}", 200)

    def test_success_rate(self):
        s = AppAPIDeveloperAPIApiDeveloperApiWebhookTestingSandbox()
        s.send_test("inst-1", "t1", "https://a.com", "push", "{}", 200)
        s.send_test("inst-1", "t2", "https://a.com", "push", "{}", 200)
        s.send_test("inst-1", "t3", "https://a.com", "push", "{}", 500)
        assert s.success_rate("inst-1") == 66.7

    def test_isolation(self):
        s = AppAPIDeveloperAPIApiDeveloperApiWebhookTestingSandbox()
        s.send_test("inst-1", "t1", "https://a.com", "push", "{}", 200)
        assert s.success_rate("inst-2") == 0.0
