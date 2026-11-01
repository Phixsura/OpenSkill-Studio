from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_event_replay_buffer import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiEventReplayBuffer, BufferedEvent,
)

class TestEventReplayBuffer:
    def test_buffer_and_replay(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiEventReplayBuffer()
        svc.buffer_event("inst-1", BufferedEvent(event_id="e1", event_type="order.created", consumer_id="c1", payload_hash="abc123", size_bytes=512))
        svc.buffer_event("inst-1", BufferedEvent(event_id="e2", event_type="order.updated", consumer_id="c1", payload_hash="def456", size_bytes=256))
        events = svc.replay_all("inst-1", "c1")
        assert len(events) == 2
        assert svc.pending_count("inst-1", "c1") == 0

    def test_eviction(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiEventReplayBuffer(max_buffer_size=100)
        for i in range(150): svc.buffer_event("inst-1", BufferedEvent(event_id=f"e{i}", event_type="x", consumer_id="c1", payload_hash=f"h{i}"))
        assert svc.total_buffered("inst-1") == 100

    def test_size_tracking(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiEventReplayBuffer()
        svc.buffer_event("inst-1", BufferedEvent(event_id="e1", event_type="x", consumer_id="c1", payload_hash="h1", size_bytes=1024))
        assert svc.buffer_size_bytes("inst-1") == 1024

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiEventReplayBuffer()
        svc.buffer_event("inst-1", BufferedEvent(event_id="e1", event_type="x", consumer_id="c1", payload_hash="h1"))
        assert svc.total_buffered("inst-2") == 0
