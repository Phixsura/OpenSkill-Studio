"""Tests for Consumer API Playground service."""
import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_playground import (
    ApiPlayground, PlaygroundRequest,
)


class TestApiPlayground:
    def test_create_collection_and_add(self):
        svc = ApiPlayground()
        svc.create_collection("c1", "Users API")
        result = svc.add_request("c1", PlaygroundRequest("r1", "List Users", "GET", "/api/users"))
        assert result["total_requests"] == 1

    def test_execute_and_history(self):
        svc = ApiPlayground()
        req = PlaygroundRequest("r1", "Get User", "GET", "/api/users/1")
        svc.execute(req, status_code=200, response_body='{"id":1}', latency_ms=45.0)
        history = svc.get_history()
        assert len(history) == 1
        assert history[0]["status_code"] == 200

    def test_history_filter_by_method(self):
        svc = ApiPlayground()
        svc.execute(PlaygroundRequest("r1", "Get", "GET", "/a"), 200)
        svc.execute(PlaygroundRequest("r2", "Post", "POST", "/b"), 201)
        history = svc.get_history(method="POST")
        assert len(history) == 1
        assert history[0]["method"] == "POST"

    def test_get_collection(self):
        svc = ApiPlayground()
        svc.create_collection("c1", "Test")
        svc.add_request("c1", PlaygroundRequest("r1", "Req 1", "GET", "/a"))
        coll = svc.get_collection("c1")
        assert coll["request_count"] == 1
        assert coll["requests"][0]["name"] == "Req 1"

    def test_list_collections(self):
        svc = ApiPlayground()
        svc.create_collection("c1", "A")
        svc.create_collection("c2", "B")
        assert len(svc.list_collections()) == 2

    def test_delete_collection(self):
        svc = ApiPlayground()
        svc.create_collection("c1", "Test")
        assert svc.delete_collection("c1")["deleted"] is True
        assert svc.get_collection("c1") is None

    def test_history_eviction(self):
        svc = ApiPlayground()
        svc._max_history = 10
        for i in range(15):
            svc.execute(PlaygroundRequest(f"r{i}", f"Req {i}", "GET", f"/api/{i}"), 200)
        assert len(svc._history) <= 10

    def test_stats(self):
        svc = ApiPlayground()
        svc.create_collection("c1", "A")
        svc.add_request("c1", PlaygroundRequest("r1", "R1", "GET", "/a"))
        svc.execute(PlaygroundRequest("r2", "R2", "POST", "/b"), 201)
        stats = svc.get_stats()
        assert stats["collections"] == 1
        assert stats["saved_requests"] == 1
        assert stats["history_entries"] == 1

    def test_duplicate_collection(self):
        svc = ApiPlayground()
        svc.create_collection("c1", "A")
        with pytest.raises(ValueError):
            svc.create_collection("c1", "B")

    def test_add_to_missing_collection(self):
        svc = ApiPlayground()
        with pytest.raises(ValueError):
            svc.add_request("missing", PlaygroundRequest("r1", "R", "GET", "/a"))

    def test_isolation(self):
        a, b = ApiPlayground(), ApiPlayground()
        a.create_collection("c1", "A")
        assert b.list_collections() == []
