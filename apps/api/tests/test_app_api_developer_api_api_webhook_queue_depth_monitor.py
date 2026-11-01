from app.services.app_api_developer_api_api_webhook_queue_depth_monitor import AppAPIDeveloperAPIApiWebhookQueueDepthMonitor

class TestQueueDepthMonitor:
    def test_record(self):
        m = AppAPIDeveloperAPIApiWebhookQueueDepthMonitor()
        s = m.record("inst-1", "https://a.com", 500, 10, 50)
        assert s.estimated_drain_seconds == 10.0

    def test_backlogged(self):
        m = AppAPIDeveloperAPIApiWebhookQueueDepthMonitor()
        m.record("inst-1", "https://a.com", 2000, 600, 10)
        m.record("inst-1", "https://b.com", 50, 5, 100)
        assert len(m.backlogged("inst-1")) == 1

    def test_total_depth(self):
        m = AppAPIDeveloperAPIApiWebhookQueueDepthMonitor()
        m.record("inst-1", "https://a.com", 100, 5, 50)
        m.record("inst-1", "https://b.com", 200, 5, 50)
        assert m.total_depth("inst-1") == 300

    def test_latest_per_dest(self):
        m = AppAPIDeveloperAPIApiWebhookQueueDepthMonitor()
        m.record("inst-1", "https://a.com", 100, 5, 50)
        m.record("inst-1", "https://a.com", 50, 3, 60)
        latest = m.latest("inst-1")
        assert len(latest) == 1
        assert latest[0].depth == 50

    def test_isolation(self):
        m = AppAPIDeveloperAPIApiWebhookQueueDepthMonitor()
        m.record("inst-1", "https://a.com", 100, 5, 50)
        assert m.total_depth("inst-2") == 0
