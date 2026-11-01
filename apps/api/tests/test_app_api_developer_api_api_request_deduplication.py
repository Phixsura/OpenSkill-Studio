import pytest
from app.services.app_api_developer_api_api_request_deduplication import AppAPIDeveloperAPIApiRequestDeduplication

class TestRequestDeduplication:
    def test_first_request(self):
        d = AppAPIDeveloperAPIApiRequestDeduplication()
        is_dup, entry = d.check_or_store("inst-1", "key-1", '{"data": 1}', 201)
        assert is_dup is False

    def test_duplicate(self):
        d = AppAPIDeveloperAPIApiRequestDeduplication()
        d.check_or_store("inst-1", "key-1", '{"data": 1}', 201)
        is_dup, entry = d.check_or_store("inst-1", "key-1", '{"data": 1}', 201)
        assert is_dup is True
        assert entry.hit_count == 1

    def test_payload_mismatch(self):
        d = AppAPIDeveloperAPIApiRequestDeduplication()
        d.check_or_store("inst-1", "key-1", '{"data": 1}', 201)
        with pytest.raises(ValueError, match="Payload mismatch"):
            d.check_or_store("inst-1", "key-1", '{"data": 2}', 201)

    def test_expired(self):
        d = AppAPIDeveloperAPIApiRequestDeduplication(ttl_seconds=0)
        d.check_or_store("inst-1", "key-1", "{}", 200)
        is_dup, _ = d.check_or_store("inst-1", "key-1", "{}", 200)
        assert is_dup is False  # expired, treated as new

    def test_stats(self):
        d = AppAPIDeveloperAPIApiRequestDeduplication()
        d.check_or_store("inst-1", "k1", "{}", 200)
        d.check_or_store("inst-1", "k1", "{}", 200)
        s = d.stats("inst-1")
        assert s["active_keys"] == 1
        assert s["duplicate_hits"] == 1
