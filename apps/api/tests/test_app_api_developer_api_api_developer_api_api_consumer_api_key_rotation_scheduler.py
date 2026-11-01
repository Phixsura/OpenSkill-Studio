import time
from app.services.app_api_developer_api_api_developer_api_api_consumer_api_key_rotation_scheduler import AppAPIDeveloperAPIApiDeveloperApiApiConsumerApiKeyRotationScheduler

class TestConsumerKeyRotation:
    def test_schedule(self):
        r = AppAPIDeveloperAPIApiDeveloperApiApiConsumerApiKeyRotationScheduler()
        s = r.schedule("inst-1", "c1", "k1", 90)
        assert s.days_until_rotation > 89

    def test_rotate(self):
        r = AppAPIDeveloperAPIApiDeveloperApiApiConsumerApiKeyRotationScheduler()
        r.schedule("inst-1", "c1", "k1", 90)
        s = r.rotate("inst-1", "c1", "k1")
        assert s.rotation_count == 1

    def test_overdue(self):
        r = AppAPIDeveloperAPIApiDeveloperApiApiConsumerApiKeyRotationScheduler()
        s = r.schedule("inst-1", "c1", "k1", 1)
        s.last_rotated_at = time.time() - 200000  # ~2 days ago
        assert len(r.overdue_keys("inst-1")) == 1

    def test_by_consumer(self):
        r = AppAPIDeveloperAPIApiDeveloperApiApiConsumerApiKeyRotationScheduler()
        r.schedule("inst-1", "c1", "k1", 90)
        r.schedule("inst-1", "c1", "k2", 30)
        r.schedule("inst-1", "c2", "k3", 60)
        assert len(r.by_consumer("inst-1", "c1")) == 2

    def test_isolation(self):
        r = AppAPIDeveloperAPIApiDeveloperApiApiConsumerApiKeyRotationScheduler()
        r.schedule("inst-1", "c1", "k1", 90)
        assert len(r.all_schedules("inst-2")) == 0
