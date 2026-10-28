"""Tests for App API Batch Request — create, results, completion."""

import pytest
from app.services.app_api_batch_request import AppAPIBatchRequest

OPS = [
    {"id": "op1", "method": "GET", "path": "/api/users"},
    {"id": "op2", "method": "POST", "path": "/api/apps"},
]


class TestCreate:
    def test_create(self):
        b = AppAPIBatchRequest()
        batch = b.create_batch("inst-1", "b1", OPS)
        assert batch.total == 2
        assert not batch.all_complete

    def test_too_many(self):
        b = AppAPIBatchRequest(max_operations=1)
        with pytest.raises(ValueError, match="Max"):
            b.create_batch("inst-1", "b1", OPS)


class TestResults:
    def test_record(self):
        b = AppAPIBatchRequest()
        b.create_batch("inst-1", "b1", OPS)
        b.record_result("inst-1", "b1", "op1", 200)
        b.record_result("inst-1", "b1", "op2", 500, "Server error")
        batch = b.get_batch("inst-1", "b1")
        assert batch.success_count == 1
        assert batch.failure_count == 1
        assert batch.all_complete is True


class TestIsolation:
    def test_cross(self):
        b = AppAPIBatchRequest()
        b.create_batch("inst-1", "b1", OPS)
        with pytest.raises(KeyError):
            b.get_batch("inst-2", "b1")
