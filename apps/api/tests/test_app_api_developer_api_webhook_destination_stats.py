from app.services.app_api_developer_api_webhook_destination_stats import AppAPIDeveloperAPIWebhookDestinationStats

class TestDestStats:
    def test_record(self):
        s = AppAPIDeveloperAPIWebhookDestinationStats()
        ds = s.record("inst-1", "https://a.com", True, 50, 200)
        assert ds.success_rate == 100.0

    def test_failing(self):
        s = AppAPIDeveloperAPIWebhookDestinationStats()
        for _ in range(5): s.record("inst-1", "https://bad.com", False, 100, 500)
        for _ in range(5): s.record("inst-1", "https://bad.com", True, 50, 200)
        assert len(s.failing_destinations("inst-1", 90)) == 1

    def test_top(self):
        s = AppAPIDeveloperAPIWebhookDestinationStats()
        for _ in range(10): s.record("inst-1", "https://busy.com", True, 50, 200)
        for _ in range(3): s.record("inst-1", "https://quiet.com", True, 50, 200)
        assert s.top_destinations("inst-1")[0].destination == "https://busy.com"

    def test_isolation(self):
        s = AppAPIDeveloperAPIWebhookDestinationStats()
        s.record("inst-1", "https://a.com", True, 50, 200)
        assert s.list_stats("inst-2") == []
