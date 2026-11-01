from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_request_mirror import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestMirror, MirrorConfig, MirrorResult,
)

class TestRequestMirror:
    def test_full_sample_always_mirrors(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestMirror()
        svc.configure("inst-1", MirrorConfig(consumer_id="c1", mirror_url="https://mirror.example.com", sample_rate=1.0))
        assert svc.should_mirror("inst-1", "c1", 12345) is True

    def test_disabled_never_mirrors(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestMirror()
        svc.configure("inst-1", MirrorConfig(consumer_id="c1", mirror_url="https://m.com", enabled=False))
        assert svc.should_mirror("inst-1", "c1", 12345) is False

    def test_record_stats(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestMirror()
        svc.record_mirror("inst-1", MirrorResult(request_id="r1", mirrored=True, mirror_status=200))
        svc.record_mirror("inst-1", MirrorResult(request_id="r2", mirrored=True, mirror_status=500))
        s = svc.stats("inst-1")
        assert s["mirrored"] == 2 and s["failed"] == 1

    def test_invalid_sample_rate(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestMirror()
        import pytest
        with pytest.raises(ValueError):
            svc.configure("inst-1", MirrorConfig(consumer_id="c1", mirror_url="https://x.example.com", sample_rate=1.5))

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestMirror()
        svc.configure("inst-1", MirrorConfig(consumer_id="c1", mirror_url="https://x.example.com"))
        assert len(svc.list_configs("inst-2")) == 0
