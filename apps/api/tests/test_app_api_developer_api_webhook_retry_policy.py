import pytest
from app.services.app_api_developer_api_webhook_retry_policy import AppAPIDeveloperAPIWebhookRetryPolicy

class TestRetryPolicy:
    def test_exponential(self):
        r = AppAPIDeveloperAPIWebhookRetryPolicy()
        r.create("inst-1", "p1", max_retries=4, base_delay_seconds=10, max_delay_seconds=3600)
        s = r.schedule("inst-1", "p1")
        assert s == [10, 20, 40, 80]

    def test_linear(self):
        r = AppAPIDeveloperAPIWebhookRetryPolicy()
        r.create("inst-1", "p1", max_retries=3, base_delay_seconds=30, max_delay_seconds=3600, strategy="linear")
        s = r.schedule("inst-1", "p1")
        assert s == [30, 60, 90]

    def test_fixed(self):
        r = AppAPIDeveloperAPIWebhookRetryPolicy()
        r.create("inst-1", "p1", max_retries=3, base_delay_seconds=60, max_delay_seconds=3600, strategy="fixed")
        s = r.schedule("inst-1", "p1")
        assert s == [60, 60, 60]

    def test_max_delay_cap(self):
        r = AppAPIDeveloperAPIWebhookRetryPolicy()
        r.create("inst-1", "p1", max_retries=5, base_delay_seconds=100, max_delay_seconds=200)
        s = r.schedule("inst-1", "p1")
        assert all(d <= 200 for d in s)

    def test_isolation(self):
        r = AppAPIDeveloperAPIWebhookRetryPolicy()
        r.create("inst-1", "p1", max_retries=3)
        assert len(r.list_policies("inst-2")) == 0
