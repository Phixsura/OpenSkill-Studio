from app.services.app_api_developer_api_api_webhook_replay_manager import AppAPIDeveloperAPIApiWebhookReplayManager

class TestReplayManager:
    def test_request_replay(self):
        m = AppAPIDeveloperAPIApiWebhookReplayManager()
        r = m.request_replay("inst-1", "r1", "d1", "https://a.com", "push")
        assert r.status == "pending"

    def test_lifecycle(self):
        m = AppAPIDeveloperAPIApiWebhookReplayManager()
        m.request_replay("inst-1", "r1", "d1", "https://a.com", "push")
        m.start_replay("inst-1", "r1")
        r = m.complete_replay("inst-1", "r1", True)
        assert r.status == "success"
        assert r.replayed_at is not None

    def test_failure(self):
        m = AppAPIDeveloperAPIApiWebhookReplayManager()
        m.request_replay("inst-1", "r1", "d1", "https://a.com", "push")
        r = m.complete_replay("inst-1", "r1", False)
        assert r.status == "failure"

    def test_pending(self):
        m = AppAPIDeveloperAPIApiWebhookReplayManager()
        m.request_replay("inst-1", "r1", "d1", "https://a.com", "push")
        m.request_replay("inst-1", "r2", "d2", "https://a.com", "issue")
        m.complete_replay("inst-1", "r1", True)
        assert len(m.pending_replays("inst-1")) == 1

    def test_stats(self):
        m = AppAPIDeveloperAPIApiWebhookReplayManager()
        m.request_replay("inst-1", "r1", "d1", "https://a.com", "push")
        m.complete_replay("inst-1", "r1", True)
        m.request_replay("inst-1", "r2", "d2", "https://a.com", "issue")
        s = m.replay_stats("inst-1")
        assert s["success"] == 1
        assert s["pending"] == 1

    def test_isolation(self):
        m = AppAPIDeveloperAPIApiWebhookReplayManager()
        m.request_replay("inst-1", "r1", "d1", "https://a.com", "push")
        assert len(m.pending_replays("inst-2")) == 0
