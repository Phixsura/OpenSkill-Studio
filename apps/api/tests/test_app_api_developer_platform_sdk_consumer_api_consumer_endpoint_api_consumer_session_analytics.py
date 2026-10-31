import pytest
from datetime import datetime, timedelta
from app.services.app_api_developer_platform_sdk_consumer_api_consumer_endpoint_api_consumer_session_analytics import (
    AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointApiConsumerSessionAnalytics, SessionRecord,
)

class TestConsumerSessionAnalytics:
    def _now(self):
        return datetime(2026, 6, 1, 12, 0, 0)

    def test_record_and_analytics(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointApiConsumerSessionAnalytics()
        svc.record_session("inst-1", SessionRecord(session_id="s1", consumer_id="c1", started_at=self._now(), ended_at=self._now() + timedelta(minutes=5), request_count=20, endpoints_visited=["/api/users", "/api/orders"]))
        analytics = svc.get_analytics("inst-1", "c1")
        assert analytics.total_sessions == 1 and analytics.avg_requests_per_session == 20

    def test_avg_duration(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointApiConsumerSessionAnalytics()
        svc.record_session("inst-1", SessionRecord(session_id="s1", consumer_id="c1", started_at=self._now(), ended_at=self._now() + timedelta(minutes=10), request_count=10))
        svc.record_session("inst-1", SessionRecord(session_id="s2", consumer_id="c1", started_at=self._now(), ended_at=self._now() + timedelta(minutes=20), request_count=30))
        analytics = svc.get_analytics("inst-1", "c1")
        assert analytics.avg_duration_seconds == 900.0  # 15 min avg

    def test_most_visited(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointApiConsumerSessionAnalytics()
        svc.record_session("inst-1", SessionRecord(session_id="s1", consumer_id="c1", started_at=self._now(), endpoints_visited=["/api/users", "/api/users", "/api/orders"]))
        analytics = svc.get_analytics("inst-1", "c1")
        assert analytics.most_visited_endpoint == "/api/users"

    def test_active_sessions(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointApiConsumerSessionAnalytics()
        svc.record_session("inst-1", SessionRecord(session_id="s1", consumer_id="c1", started_at=self._now()))  # no ended_at
        svc.record_session("inst-1", SessionRecord(session_id="s2", consumer_id="c1", started_at=self._now(), ended_at=self._now()))
        active = svc.get_active_sessions("inst-1", "c1")
        assert len(active) == 1

    def test_empty(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointApiConsumerSessionAnalytics()
        analytics = svc.get_analytics("inst-1", "c1")
        assert analytics.total_sessions == 0

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointApiConsumerSessionAnalytics()
        svc.record_session("inst-1", SessionRecord(session_id="s1", consumer_id="c1", started_at=self._now()))
        assert svc.get_analytics("inst-2", "c1").total_sessions == 0
