from app.services.app_api_developer_api_api_webhook_correlation_tracker import AppAPIDeveloperAPIApiWebhookCorrelationTracker

class TestCorrelationTracker:
    def test_track(self):
        t = AppAPIDeveloperAPIApiWebhookCorrelationTracker()
        c = t.track("inst-1", "corr-1", "e1", "push")
        assert c.event_count == 1

    def test_chain_growth(self):
        t = AppAPIDeveloperAPIApiWebhookCorrelationTracker()
        t.track("inst-1", "corr-1", "e1", "push")
        t.track("inst-1", "corr-1", "e2", "build")
        c = t.track("inst-1", "corr-1", "e3", "deploy")
        assert c.event_count == 3
        assert c.events[-1].sequence == 2

    def test_long_chains(self):
        t = AppAPIDeveloperAPIApiWebhookCorrelationTracker()
        for i in range(6): t.track("inst-1", "long", f"e{i}", "event")
        for i in range(2): t.track("inst-1", "short", f"e{i}", "event")
        assert len(t.long_chains("inst-1", 5)) == 1

    def test_total(self):
        t = AppAPIDeveloperAPIApiWebhookCorrelationTracker()
        t.track("inst-1", "c1", "e1", "push")
        t.track("inst-1", "c2", "e2", "issue")
        assert t.total_chains("inst-1") == 2

    def test_isolation(self):
        t = AppAPIDeveloperAPIApiWebhookCorrelationTracker()
        t.track("inst-1", "c1", "e1", "push")
        assert t.total_chains("inst-2") == 0
