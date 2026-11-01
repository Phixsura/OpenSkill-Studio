import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_webhook_event_replay_policy import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookEventReplayPolicy, ReplayPolicy,
)

class TestWebhookEventReplayPolicy:
    def test_can_replay(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookEventReplayPolicy()
        svc.set_policy("inst-1", ReplayPolicy(consumer_id="c1", max_replays_per_event=3))
        assert svc.can_replay("inst-1", "c1", "ev1") is True

    def test_max_replays(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookEventReplayPolicy()
        svc.set_policy("inst-1", ReplayPolicy(consumer_id="c1", max_replays_per_event=2))
        svc.record_replay("inst-1", "c1", "ev1")
        svc.record_replay("inst-1", "c1", "ev1")
        assert svc.can_replay("inst-1", "c1", "ev1") is False

    def test_exceed_max_raises(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookEventReplayPolicy()
        svc.set_policy("inst-1", ReplayPolicy(consumer_id="c1", max_replays_per_event=1))
        svc.record_replay("inst-1", "c1", "ev1")
        with pytest.raises(ValueError, match="Max replays"):
            svc.record_replay("inst-1", "c1", "ev1")

    def test_no_policy_denies(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookEventReplayPolicy()
        assert svc.can_replay("inst-1", "c1", "ev1") is False

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookEventReplayPolicy()
        svc.set_policy("inst-1", ReplayPolicy(consumer_id="c1"))
        assert len(svc.list_policies("inst-2")) == 0
