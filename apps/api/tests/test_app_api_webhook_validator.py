from app.services.app_api_webhook_validator import AppAPIWebhookValidator

class TestValidate:
    def test_valid(self):
        v = AppAPIWebhookValidator()
        assert v.validate_config("https://a.com", ["push"]) == []

    def test_http_rejected(self):
        v = AppAPIWebhookValidator()
        issues = v.validate_config("http://a.com", ["push"])
        assert any("HTTPS" in i.message for i in issues)

    def test_no_events(self):
        v = AppAPIWebhookValidator()
        issues = v.validate_config("https://a.com", [])
        assert len(issues) == 1

    def test_short_secret(self):
        v = AppAPIWebhookValidator()
        issues = v.validate_config("https://a.com", ["push"], "short")
        assert any("16" in i.message for i in issues)
