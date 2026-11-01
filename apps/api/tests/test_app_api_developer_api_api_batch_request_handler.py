import pytest
from app.services.app_api_developer_api_api_batch_request_handler import AppAPIDeveloperAPIApiBatchRequestHandler

class TestBatchRequestHandler:
    def test_execute(self):
        h = AppAPIDeveloperAPIApiBatchRequestHandler()
        r = h.execute("inst-1", "b1", [
            {"request_id": "r1", "method": "GET", "path": "/api/users", "status_code": 200},
            {"request_id": "r2", "method": "POST", "path": "/api/users", "status_code": 201},
        ])
        assert r.total == 2
        assert r.succeeded == 2

    def test_partial_failure(self):
        h = AppAPIDeveloperAPIApiBatchRequestHandler()
        r = h.execute("inst-1", "b1", [
            {"request_id": "r1", "status_code": 200},
            {"request_id": "r2", "status_code": 500},
        ])
        assert r.succeeded == 1
        assert r.failed == 1

    def test_max_size(self):
        h = AppAPIDeveloperAPIApiBatchRequestHandler(max_batch_size=2)
        with pytest.raises(ValueError, match="max size"):
            h.execute("inst-1", "b1", [{"request_id": f"r{i}"} for i in range(5)])

    def test_empty_batch(self):
        h = AppAPIDeveloperAPIApiBatchRequestHandler()
        with pytest.raises(ValueError):
            h.execute("inst-1", "b1", [])

    def test_isolation(self):
        h = AppAPIDeveloperAPIApiBatchRequestHandler()
        h.execute("inst-1", "b1", [{"request_id": "r1"}])
        assert len(h.recent_batches("inst-2")) == 0
