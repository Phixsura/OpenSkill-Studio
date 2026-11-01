import pytest
from app.services.app_api_consumer_quota import AppAPIConsumerQuota

class TestQuota:
    def test_set_consume(self):
        q = AppAPIConsumerQuota()
        q.set_quota("inst-1", "c1", 100)
        cq = q.consume("inst-1", "c1", 30)
        assert cq.remaining == 70

    def test_exhausted(self):
        q = AppAPIConsumerQuota()
        q.set_quota("inst-1", "c1", 5)
        q.consume("inst-1", "c1", 5)
        with pytest.raises(ValueError, match="exhausted"):
            q.consume("inst-1", "c1", 1)

    def test_reset(self):
        q = AppAPIConsumerQuota()
        q.set_quota("inst-1", "c1", 100)
        q.consume("inst-1", "c1", 50)
        q.reset_all("inst-1")
        assert q.list_quotas("inst-1")[0].daily_used == 0

    def test_exhausted_list(self):
        q = AppAPIConsumerQuota()
        q.set_quota("inst-1", "c1", 1)
        q.set_quota("inst-1", "c2", 100)
        q.consume("inst-1", "c1", 1)
        assert len(q.exhausted_consumers("inst-1")) == 1

    def test_isolation(self):
        q = AppAPIConsumerQuota()
        q.set_quota("inst-1", "c1", 100)
        assert q.list_quotas("inst-2") == []
