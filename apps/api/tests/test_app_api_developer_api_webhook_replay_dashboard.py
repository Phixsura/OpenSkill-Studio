from app.services.app_api_developer_api_webhook_replay_dashboard import AppAPIDeveloperAPIWebhookReplayDashboard

class TestReplayDash:
    def test_success_rate(self):
        d = AppAPIDeveloperAPIWebhookReplayDashboard()
        rd = d.update("inst-1", successful_replays=90, failed_replays=10)
        assert rd.replay_success_rate == 90.0

    def test_default(self):
        d = AppAPIDeveloperAPIWebhookReplayDashboard()
        assert d.get("inst-1").replay_success_rate == 100.0

    def test_isolation(self):
        d = AppAPIDeveloperAPIWebhookReplayDashboard()
        d.update("inst-1", total_replayed=50)
        assert d.get("inst-2").total_replayed == 0
