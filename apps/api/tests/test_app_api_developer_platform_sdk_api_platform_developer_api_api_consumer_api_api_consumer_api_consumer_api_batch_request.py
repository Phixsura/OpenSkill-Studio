import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_batch_request import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiBatchRequest, BatchItem,
)

class TestConsumerApiBatchRequest:
    def test_basic_batch(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiBatchRequest()
        items = [BatchItem(item_id="1", method="GET", path="/api/users"), BatchItem(item_id="2", method="POST", path="/api/orders")]
        result = svc.execute("inst-1", "c1", items)
        assert result.total == 2 and result.succeeded == 2

    def test_invalid_method(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiBatchRequest()
        result = svc.execute("inst-1", "c1", [BatchItem(item_id="1", method="HACK", path="/api")])
        assert result.failed == 1 and result.results[0].status_code == 400

    def test_max_size(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiBatchRequest(max_batch_size=2)
        items = [BatchItem(item_id=str(i), method="GET", path="/api") for i in range(3)]
        with pytest.raises(ValueError, match="exceeds max"):
            svc.execute("inst-1", "c1", items)

    def test_duplicate_ids(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiBatchRequest()
        with pytest.raises(ValueError, match="Duplicate"):
            svc.execute("inst-1", "c1", [BatchItem(item_id="1", method="GET", path="/a"), BatchItem(item_id="1", method="GET", path="/b")])

    def test_stats(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiBatchRequest()
        svc.execute("inst-1", "c1", [BatchItem(item_id="1", method="GET", path="/api")])
        stats = svc.get_stats("inst-1", "c1")
        assert stats["batches"] == 1 and stats["items"] == 1

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiBatchRequest()
        svc.execute("inst-1", "c1", [BatchItem(item_id="1", method="GET", path="/api")])
        assert svc.get_stats("inst-2", "c1")["batches"] == 0
