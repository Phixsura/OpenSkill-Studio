import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_request_bulkhead import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestBulkhead, BulkheadPartition,
)

class TestRequestBulkhead:
    def test_acquire_and_release(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestBulkhead()
        svc.create_partition("inst-1", BulkheadPartition(partition_id="p1", name="Critical", max_concurrent=3))
        assert svc.try_acquire("inst-1", "p1") is True
        assert svc.utilization("inst-1", "p1") > 0
        svc.release("inst-1", "p1")

    def test_rejection(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestBulkhead()
        svc.create_partition("inst-1", BulkheadPartition(partition_id="p1", name="Limited", max_concurrent=2))
        svc.try_acquire("inst-1", "p1")
        svc.try_acquire("inst-1", "p1")
        assert svc.try_acquire("inst-1", "p1") is False
        p = svc._partitions[("inst-1", "p1")]
        assert p.rejected == 1

    def test_no_partition_allows(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestBulkhead()
        assert svc.try_acquire("inst-1", "nonexistent") is True

    def test_duplicate_partition(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestBulkhead()
        svc.create_partition("inst-1", BulkheadPartition(partition_id="p1", name="X", max_concurrent=5))
        with pytest.raises(ValueError, match="exists"):
            svc.create_partition("inst-1", BulkheadPartition(partition_id="p1", name="Y", max_concurrent=5))

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestBulkhead()
        svc.create_partition("inst-1", BulkheadPartition(partition_id="p1", name="X", max_concurrent=5))
        assert len(svc.list_partitions("inst-2")) == 0
