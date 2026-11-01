import pytest
from app.services.app_api_developer_platform_sdk_api_platform_api_webhook_event_replay_scheduler import AppAPIDeveloperPlatformSDKApiPlatformApiWebhookEventReplayScheduler

class TestReplayScheduler:
    def test_schedule(self):
        s = AppAPIDeveloperPlatformSDKApiPlatformApiWebhookEventReplayScheduler()
        j = s.schedule("inst-1", "j1", "https://a.com", ["e1", "e2", "e3"])
        assert j.total == 3
        assert j.status == "pending"

    def test_empty_events_rejected(self):
        s = AppAPIDeveloperPlatformSDKApiPlatformApiWebhookEventReplayScheduler()
        with pytest.raises(ValueError):
            s.schedule("inst-1", "j1", "https://a.com", [])

    def test_process_to_completion(self):
        s = AppAPIDeveloperPlatformSDKApiPlatformApiWebhookEventReplayScheduler()
        s.schedule("inst-1", "j1", "https://a.com", ["e1", "e2"])
        s.process("inst-1", "j1", True)
        j = s.process("inst-1", "j1", True)
        assert j.status == "completed"
        assert j.progress_pct == 100.0

    def test_process_with_failure(self):
        s = AppAPIDeveloperPlatformSDKApiPlatformApiWebhookEventReplayScheduler()
        s.schedule("inst-1", "j1", "https://a.com", ["e1", "e2"])
        s.process("inst-1", "j1", True)
        j = s.process("inst-1", "j1", False)
        assert j.status == "failed"

    def test_active_jobs(self):
        s = AppAPIDeveloperPlatformSDKApiPlatformApiWebhookEventReplayScheduler()
        s.schedule("inst-1", "j1", "https://a.com", ["e1"])
        s.schedule("inst-1", "j2", "https://b.com", ["e2"])
        s.process("inst-1", "j1", True)  # completes j1
        assert len(s.active_jobs("inst-1")) == 1

    def test_isolation(self):
        s = AppAPIDeveloperPlatformSDKApiPlatformApiWebhookEventReplayScheduler()
        s.schedule("inst-1", "j1", "https://a.com", ["e1"])
        assert len(s.all_jobs("inst-2")) == 0
