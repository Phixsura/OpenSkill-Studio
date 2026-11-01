"""Tests for Endpoint Batch Processor service."""
import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_batch_processor import (
    BatchProcessor, BatchRequest, BatchResult,
)


class TestBatchProcessor:
    def test_create_and_execute(self):
        svc = BatchProcessor()
        reqs = [BatchRequest(f"r{i}", "ep1", "GET") for i in range(3)]
        svc.create_batch("b1", "c1", reqs)
        result = svc.execute("b1")
        assert result["status"] == "completed"
        assert result["total"] == 3
        assert result["succeeded"] == 3

    def test_with_failures(self):
        svc = BatchProcessor()
        reqs = [BatchRequest("r1", "ep1", "GET"), BatchRequest("r2", "ep1", "POST")]
        svc.create_batch("b1", "c1", reqs)
        def handler(req):
            if req.method == "POST":
                return BatchResult(req.request_id, 500, error="server error")
            return BatchResult(req.request_id, 200)
        result = svc.execute("b1", handler=handler)
        assert result["failed"] == 1
        assert result["status"] == "failed"

    def test_get_results(self):
        svc = BatchProcessor()
        svc.create_batch("b1", "c1", [BatchRequest("r1", "ep1", "GET")])
        svc.execute("b1")
        results = svc.get_results("b1")
        assert len(results["results"]) == 1
        assert results["results"][0]["status_code"] == 200

    def test_sequential_mode(self):
        svc = BatchProcessor()
        reqs = [BatchRequest("r1", "ep1", "GET")]
        svc.create_batch("b1", "c1", reqs, mode="sequential")
        job = svc.get_job("b1")
        assert job["mode"] == "sequential"

    def test_max_size(self):
        svc = BatchProcessor()
        svc.configure(max_batch_size=5)
        reqs = [BatchRequest(f"r{i}", "ep1", "GET") for i in range(10)]
        with pytest.raises(ValueError, match="max size"):
            svc.create_batch("b1", "c1", reqs)

    def test_empty_batch(self):
        svc = BatchProcessor()
        with pytest.raises(ValueError):
            svc.create_batch("b1", "c1", [])

    def test_duplicate_batch(self):
        svc = BatchProcessor()
        svc.create_batch("b1", "c1", [BatchRequest("r1", "ep1", "GET")])
        with pytest.raises(ValueError):
            svc.create_batch("b1", "c1", [BatchRequest("r2", "ep1", "GET")])

    def test_cancel(self):
        svc = BatchProcessor()
        svc.create_batch("b1", "c1", [BatchRequest("r1", "ep1", "GET")])
        result = svc.cancel("b1")
        assert result["cancelled"] is True

    def test_list_jobs(self):
        svc = BatchProcessor()
        svc.create_batch("b1", "c1", [BatchRequest("r1", "ep1", "GET")])
        svc.create_batch("b2", "c2", [BatchRequest("r2", "ep1", "GET")])
        jobs = svc.list_jobs(consumer_id="c1")
        assert len(jobs) == 1

    def test_already_completed(self):
        svc = BatchProcessor()
        svc.create_batch("b1", "c1", [BatchRequest("r1", "ep1", "GET")])
        svc.execute("b1")
        with pytest.raises(ValueError):
            svc.execute("b1")

    def test_isolation(self):
        a, b = BatchProcessor(), BatchProcessor()
        a.create_batch("b1", "c1", [BatchRequest("r1", "ep1", "GET")])
        assert b.get_job("b1") is None
