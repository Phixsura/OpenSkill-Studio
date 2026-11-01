import pytest
from app.services.app_api_developer_api_api_developer_api_api_usage_alert import AppAPIDeveloperAPIApiDeveloperApiApiUsageAlert

class TestUsageAlert:
    def test_create(self):
        a = AppAPIDeveloperAPIApiDeveloperApiApiUsageAlert()
        al = a.create("inst-1", "a1", "error_rate", 5.0, "gt")
        assert al.triggered is False

    def test_trigger(self):
        a = AppAPIDeveloperAPIApiDeveloperApiApiUsageAlert()
        a.create("inst-1", "a1", "error_rate", 5.0, "gt")
        al = a.evaluate("inst-1", "a1", 10.0)
        assert al.triggered is True
        assert al.triggered_at is not None

    def test_no_trigger(self):
        a = AppAPIDeveloperAPIApiDeveloperApiApiUsageAlert()
        a.create("inst-1", "a1", "error_rate", 5.0, "gt")
        al = a.evaluate("inst-1", "a1", 2.0)
        assert al.triggered is False

    def test_triggered_list(self):
        a = AppAPIDeveloperAPIApiDeveloperApiApiUsageAlert()
        a.create("inst-1", "a1", "error_rate", 5.0, "gt")
        a.create("inst-1", "a2", "latency_p99", 1000, "gt")
        a.evaluate("inst-1", "a1", 10.0)
        a.evaluate("inst-1", "a2", 500)
        assert len(a.triggered_alerts("inst-1")) == 1

    def test_isolation(self):
        a = AppAPIDeveloperAPIApiDeveloperApiApiUsageAlert()
        a.create("inst-1", "a1", "api_calls", 100000, "gt")
        assert len(a.all_alerts("inst-2")) == 0
