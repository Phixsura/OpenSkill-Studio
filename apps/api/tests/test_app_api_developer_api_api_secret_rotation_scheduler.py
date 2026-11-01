import time, pytest
from app.services.app_api_developer_api_api_secret_rotation_scheduler import AppAPIDeveloperAPIApiSecretRotationScheduler

class TestSecretRotationScheduler:
    def test_schedule(self):
        s = AppAPIDeveloperAPIApiSecretRotationScheduler()
        r = s.schedule("inst-1", "s1", "api_key", 90)
        assert r.days_until_rotation > 89

    def test_invalid_type(self):
        s = AppAPIDeveloperAPIApiSecretRotationScheduler()
        with pytest.raises(ValueError):
            s.schedule("inst-1", "s1", "password", 30)

    def test_rotate(self):
        s = AppAPIDeveloperAPIApiSecretRotationScheduler()
        s.schedule("inst-1", "s1", "api_key", 90)
        r = s.rotate("inst-1", "s1")
        assert r.rotation_count == 1

    def test_overdue(self):
        s = AppAPIDeveloperAPIApiSecretRotationScheduler()
        r = s.schedule("inst-1", "s1", "api_key", 1)
        r.next_rotation_at = time.time() - 1  # force overdue
        assert len(s.overdue("inst-1")) == 1

    def test_isolation(self):
        s = AppAPIDeveloperAPIApiSecretRotationScheduler()
        s.schedule("inst-1", "s1", "api_key", 90)
        assert len(s.all_schedules("inst-2")) == 0
