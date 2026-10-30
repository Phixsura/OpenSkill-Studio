import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_error_page import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiErrorPage, ErrorTemplate,
)

class TestConsumerApiErrorPage:
    def test_default_template(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiErrorPage()
        svc.set_default("inst-1", ErrorTemplate(status_code=404, error_code="NOT_FOUND", title="Not Found", message_template="Resource {{detail}} not found", docs_url="https://docs.example.com/404"))
        resp = svc.render("inst-1", "c1", 404, detail="/api/users/999")
        assert resp.error_code == "NOT_FOUND" and "/api/users/999" in resp.message

    def test_consumer_override(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiErrorPage()
        svc.set_default("inst-1", ErrorTemplate(status_code=429, error_code="RATE_LIMITED", title="Too Many Requests", message_template="Slow down"))
        svc.set_consumer_override("inst-1", "c1", ErrorTemplate(status_code=429, error_code="RATE_LIMITED", title="Rate Limited", message_template="You hit your limit. {{detail}}", support_email="support@c1.com"))
        resp = svc.render("inst-1", "c1", 429, detail="Retry in 60s")
        assert resp.support_email == "support@c1.com" and "Retry in 60s" in resp.message

    def test_fallback(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiErrorPage()
        resp = svc.render("inst-1", "c1", 500, detail="Internal error")
        assert resp.error_code == "ERR_500" and "Internal error" in resp.message

    def test_invalid_status(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiErrorPage()
        with pytest.raises(ValueError, match="4xx or 5xx"):
            svc.set_default("inst-1", ErrorTemplate(status_code=200, error_code="OK", title="OK", message_template="success"))

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiErrorPage()
        svc.set_default("inst-1", ErrorTemplate(status_code=404, error_code="NF", title="NF", message_template="x"))
        assert len(svc.list_templates("inst-2")) == 0
