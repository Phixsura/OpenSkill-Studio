import pytest
from datetime import datetime
from app.services.app_api_developer_platform_sdk_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_api_consumer_api_consumer_api_api_consumer_api_sdk_download_tracker import (
    AppAPIDeveloperPlatformSDKConsumerApiSdkDownloadTracker, SDKDownload,
)

class TestSdkDownloadTracker:
    def _now(self):
        return datetime(2026, 6, 1)

    def test_record_and_stats(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiSdkDownloadTracker()
        svc.record("inst-1", SDKDownload(download_id="d1", consumer_id="c1", sdk_language="typescript", sdk_version="1.0.0", timestamp=self._now()))
        svc.record("inst-1", SDKDownload(download_id="d2", consumer_id="c1", sdk_language="python", sdk_version="1.0.0", timestamp=self._now()))
        svc.record("inst-1", SDKDownload(download_id="d3", consumer_id="c2", sdk_language="typescript", sdk_version="1.1.0", timestamp=self._now()))
        stats = svc.get_stats("inst-1")
        assert stats.total_downloads == 3 and stats.most_popular_language == "typescript"

    def test_by_version(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiSdkDownloadTracker()
        svc.record("inst-1", SDKDownload(download_id="d1", consumer_id="c1", sdk_language="python", sdk_version="1.0.0", timestamp=self._now()))
        svc.record("inst-1", SDKDownload(download_id="d2", consumer_id="c1", sdk_language="python", sdk_version="2.0.0", timestamp=self._now()))
        stats = svc.get_stats("inst-1")
        assert stats.by_version["1.0.0"] == 1 and stats.by_version["2.0.0"] == 1

    def test_consumer_downloads(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiSdkDownloadTracker()
        svc.record("inst-1", SDKDownload(download_id="d1", consumer_id="c1", sdk_language="go", sdk_version="1.0", timestamp=self._now()))
        svc.record("inst-1", SDKDownload(download_id="d2", consumer_id="c2", sdk_language="go", sdk_version="1.0", timestamp=self._now()))
        assert len(svc.get_consumer_downloads("inst-1", "c1")) == 1

    def test_invalid_language(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiSdkDownloadTracker()
        with pytest.raises(ValueError, match="Invalid language"):
            svc.record("inst-1", SDKDownload(download_id="d1", consumer_id="c1", sdk_language="cobol", sdk_version="1.0", timestamp=self._now()))

    def test_empty_stats(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiSdkDownloadTracker()
        assert svc.get_stats("inst-1").total_downloads == 0

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiSdkDownloadTracker()
        svc.record("inst-1", SDKDownload(download_id="d1", consumer_id="c1", sdk_language="typescript", sdk_version="1.0", timestamp=self._now()))
        assert svc.get_stats("inst-2").total_downloads == 0
