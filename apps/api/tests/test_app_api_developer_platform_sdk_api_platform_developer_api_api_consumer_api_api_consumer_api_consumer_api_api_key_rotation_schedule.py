import pytest
from datetime import datetime, timedelta
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_api_key_rotation_schedule import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiKeyRotationSchedule, RotationSchedule,
)

class TestConsumerApiKeyRotationSchedule:
    def _now(self):
        return datetime(2026, 6, 1)

    def test_not_due(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiKeyRotationSchedule()
        svc.set_schedule("inst-1", RotationSchedule(schedule_id="s1", consumer_id="c1", key_id="k1", interval_days=90, last_rotated_at=self._now()))
        check = svc.check("inst-1", "c1", "k1", self._now() + timedelta(days=10))
        assert not check.due and check.days_until == 80

    def test_due(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiKeyRotationSchedule()
        svc.set_schedule("inst-1", RotationSchedule(schedule_id="s1", consumer_id="c1", key_id="k1", interval_days=30, last_rotated_at=self._now()))
        check = svc.check("inst-1", "c1", "k1", self._now() + timedelta(days=35))
        assert check.due

    def test_notify_window(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiKeyRotationSchedule()
        svc.set_schedule("inst-1", RotationSchedule(schedule_id="s1", consumer_id="c1", key_id="k1", interval_days=30, last_rotated_at=self._now(), notify_days_before=7))
        check = svc.check("inst-1", "c1", "k1", self._now() + timedelta(days=25))
        assert check.notify and not check.due

    def test_mark_rotated(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiKeyRotationSchedule()
        svc.set_schedule("inst-1", RotationSchedule(schedule_id="s1", consumer_id="c1", key_id="k1", interval_days=30, last_rotated_at=self._now()))
        svc.mark_rotated("inst-1", "c1", "k1", self._now() + timedelta(days=30))
        check = svc.check("inst-1", "c1", "k1", self._now() + timedelta(days=31))
        assert not check.due

    def test_list_due(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiKeyRotationSchedule()
        svc.set_schedule("inst-1", RotationSchedule(schedule_id="s1", consumer_id="c1", key_id="k1", interval_days=10, last_rotated_at=self._now()))
        svc.set_schedule("inst-1", RotationSchedule(schedule_id="s2", consumer_id="c1", key_id="k2", interval_days=90, last_rotated_at=self._now()))
        due = svc.list_due("inst-1", self._now() + timedelta(days=12))
        assert len(due) == 1 and due[0].key_id == "k1"

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiKeyRotationSchedule()
        svc.set_schedule("inst-1", RotationSchedule(schedule_id="s1", consumer_id="c1", key_id="k1", interval_days=1, last_rotated_at=self._now()))
        assert len(svc.list_schedules("inst-2", "c1")) == 0
