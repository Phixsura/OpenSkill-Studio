import pytest
from datetime import datetime
from app.services.app_api_developer_platform_sdk_consumer_api_consumer_endpoint_api_consumer_api_playground_v2 import (
    AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointApiConsumerApiPlaygroundV2, PlaygroundCollection, PlaygroundRequest,
)

class TestApiPlaygroundV2:
    def _now(self):
        return datetime(2026, 6, 1)

    def test_create_collection(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointApiConsumerApiPlaygroundV2()
        coll = svc.create_collection("inst-1", "c1", PlaygroundCollection(collection_id="col1", name="Auth Tests"))
        assert coll.name == "Auth Tests"

    def test_add_request(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointApiConsumerApiPlaygroundV2()
        svc.create_collection("inst-1", "c1", PlaygroundCollection(collection_id="col1", name="Tests"))
        svc.add_request("inst-1", "c1", "col1", PlaygroundRequest(request_id="r1", name="List Users", method="GET", path="/api/users"))
        colls = svc.list_collections("inst-1", "c1")
        assert len(colls[0].requests) == 1

    def test_execute(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointApiConsumerApiPlaygroundV2()
        result = svc.execute("inst-1", "c1", PlaygroundRequest(request_id="r1", name="Test", method="GET", path="/api"), self._now())
        assert result.status_code == 200

    def test_history(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointApiConsumerApiPlaygroundV2()
        svc.execute("inst-1", "c1", PlaygroundRequest(request_id="r1", name="A", method="GET", path="/a"), self._now())
        svc.execute("inst-1", "c1", PlaygroundRequest(request_id="r2", name="B", method="POST", path="/b"), self._now())
        history = svc.get_history("inst-1", "c1")
        assert len(history) == 2

    def test_duplicate_collection(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointApiConsumerApiPlaygroundV2()
        svc.create_collection("inst-1", "c1", PlaygroundCollection(collection_id="col1", name="X"))
        with pytest.raises(ValueError, match="already exists"):
            svc.create_collection("inst-1", "c1", PlaygroundCollection(collection_id="col1", name="Y"))

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointApiConsumerApiPlaygroundV2()
        svc.create_collection("inst-1", "c1", PlaygroundCollection(collection_id="col1", name="X"))
        assert len(svc.list_collections("inst-2", "c1")) == 0
