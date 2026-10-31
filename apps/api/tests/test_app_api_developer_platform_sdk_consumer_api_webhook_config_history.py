import pytest
from datetime import datetime
from app.services.app_api_developer_platform_sdk_consumer_api_consumer_api_consumer_api_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_api_consumer_api_consumer_api_consumer_api_api_consumer_api_api_consumer_api_consumer_api_webhook_config_history import (
    AppAPIDeveloperPlatformSDKConsumerApiWebhookConfigHistory, ConfigChange,
)

class TestWebhookConfigHistory:
    def _now(self):
        return datetime(2026, 6, 1)

    def test_record_and_history(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiWebhookConfigHistory()
        svc.record_change("inst-1", "c1", ConfigChange(change_id="ch1", webhook_id="w1", field_name="url", old_value="https://old.com", new_value="https://new.com", changed_by="admin", timestamp=self._now()))
        history = svc.get_history("inst-1", "c1", "w1")
        assert history.total_changes == 1 and history.recent_changes[0].field_name == "url"

    def test_most_changed_field(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiWebhookConfigHistory()
        svc.record_change("inst-1", "c1", ConfigChange(change_id="ch1", webhook_id="w1", field_name="url", old_value="a", new_value="b", changed_by="x", timestamp=self._now()))
        svc.record_change("inst-1", "c1", ConfigChange(change_id="ch2", webhook_id="w1", field_name="url", old_value="b", new_value="c", changed_by="x", timestamp=self._now()))
        svc.record_change("inst-1", "c1", ConfigChange(change_id="ch3", webhook_id="w1", field_name="secret", old_value="old", new_value="new", changed_by="x", timestamp=self._now()))
        assert svc.get_history("inst-1", "c1", "w1").most_changed_field == "url"

    def test_field_history(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiWebhookConfigHistory()
        svc.record_change("inst-1", "c1", ConfigChange(change_id="ch1", webhook_id="w1", field_name="url", old_value="a", new_value="b", changed_by="x", timestamp=self._now()))
        svc.record_change("inst-1", "c1", ConfigChange(change_id="ch2", webhook_id="w1", field_name="secret", old_value="s1", new_value="s2", changed_by="x", timestamp=self._now()))
        assert len(svc.get_field_history("inst-1", "c1", "w1", "url")) == 1

    def test_rollback_to(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiWebhookConfigHistory()
        svc.record_change("inst-1", "c1", ConfigChange(change_id="ch1", webhook_id="w1", field_name="url", old_value="https://old.com", new_value="https://new.com", changed_by="admin", timestamp=self._now()))
        change = svc.rollback_to("inst-1", "c1", "w1", "ch1")
        assert change is not None and change.old_value == "https://old.com"

    def test_empty_history(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiWebhookConfigHistory()
        assert svc.get_history("inst-1", "c1", "w1").total_changes == 0

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiWebhookConfigHistory()
        svc.record_change("inst-1", "c1", ConfigChange(change_id="ch1", webhook_id="w1", field_name="x", old_value="a", new_value="b", changed_by="x", timestamp=self._now()))
        assert svc.get_history("inst-2", "c1", "w1").total_changes == 0
