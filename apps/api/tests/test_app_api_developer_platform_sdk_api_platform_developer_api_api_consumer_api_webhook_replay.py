import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_webhook_replay import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiWebhookReplay, ReplayRequest, ReplayStatus,
)

class TestWebhookReplay:
    def test_request_and_complete(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiWebhookReplay()
        svc.request_replay("inst-1", ReplayRequest(replay_id="r1", original_event_id="ev1", consumer_id="c1", endpoint="/hook"))
        r = svc.complete_replay("inst-1", "r1", 200)
        assert r.status == ReplayStatus.SUCCESS

    def test_max_replays(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiWebhookReplay(max_replays_per_event=2)
        svc.request_replay("inst-1", ReplayRequest(replay_id="r1", original_event_id="ev1", consumer_id="c1", endpoint="/h"))
        svc.request_replay("inst-1", ReplayRequest(replay_id="r2", original_event_id="ev1", consumer_id="c1", endpoint="/h"))
        with pytest.raises(ValueError, match="Max"):
            svc.request_replay("inst-1", ReplayRequest(replay_id="r3", original_event_id="ev1", consumer_id="c1", endpoint="/h"))

    def test_stats(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiWebhookReplay()
        svc.request_replay("inst-1", ReplayRequest(replay_id="r1", original_event_id="ev1", consumer_id="c1", endpoint="/h"))
        svc.complete_replay("inst-1", "r1", 200)
        svc.request_replay("inst-1", ReplayRequest(replay_id="r2", original_event_id="ev2", consumer_id="c1", endpoint="/h"))
        stats = svc.replay_stats("inst-1")
        assert stats["success"] == 1 and stats["pending"] == 1

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiWebhookReplay()
        svc.request_replay("inst-1", ReplayRequest(replay_id="r1", original_event_id="ev1", consumer_id="c1", endpoint="/h"))
        assert svc.replay_count("inst-2") == 0
