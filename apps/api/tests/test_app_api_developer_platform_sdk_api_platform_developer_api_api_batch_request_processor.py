import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_batch_request_processor import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiBatchRequestProcessor, BatchItem,
)

class TestApiBatchRequestProcessor:
    def test_process_batch(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiBatchRequestProcessor()
        items = [BatchItem(item_id="i1", method="GET", path="/users"), BatchItem(item_id="i2", method="POST", path="/orders")]
        resp = svc.process("inst-1", "b1", items)
        assert len(resp.results) == 2
        assert resp.success_count == 2
        assert resp.error_count == 0

    def test_max_batch_size(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiBatchRequestProcessor(max_batch_size=5)
        items = [BatchItem(item_id=f"i{i}", method="GET", path="/a") for i in range(10)]
        with pytest.raises(ValueError, match="exceeds max"):
            svc.process("inst-1", "b1", items)

    def test_body_truncation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiBatchRequestProcessor(max_body_size=256)
        items = [BatchItem(item_id="i1", method="POST", path="/a", body="x" * 500)]
        resp = svc.process("inst-1", "b1", items)
        assert resp.results[0].status_code == 200

    def test_get_batch_history(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiBatchRequestProcessor()
        svc.process("inst-1", "b1", [BatchItem(item_id="i1", method="GET", path="/a")])
        resp = svc.get_batch("inst-1", "b1")
        assert resp.batch_id == "b1"

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiBatchRequestProcessor()
        svc.process("inst-1", "b1", [BatchItem(item_id="i1", method="GET", path="/a")])
        assert svc.batch_count("inst-2") == 0
