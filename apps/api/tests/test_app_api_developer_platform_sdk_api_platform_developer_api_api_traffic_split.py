import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_traffic_split import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiTrafficSplit, SplitConfig, TrafficTarget,
)

class TestApiTrafficSplit:
    def test_create_and_resolve(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiTrafficSplit()
        split = SplitConfig(split_id="s1", endpoint="/api", targets=[
            TrafficTarget(version="v1", weight=80, upstream="http://v1"),
            TrafficTarget(version="v2", weight=20, upstream="http://v2"),
        ])
        svc.create_split("inst-1", split)
        target = svc.resolve("inst-1", "/api", "consumer-123")
        assert target is not None
        assert target.version in ("v1", "v2")

    def test_sticky_routing(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiTrafficSplit()
        split = SplitConfig(split_id="s1", endpoint="/api", sticky=True, targets=[
            TrafficTarget(version="v1", weight=50, upstream="http://v1"),
            TrafficTarget(version="v2", weight=50, upstream="http://v2"),
        ])
        svc.create_split("inst-1", split)
        results = {svc.resolve("inst-1", "/api", "c1").version for _ in range(10)}
        assert len(results) == 1  # same consumer always gets same version

    def test_weights_must_sum_100(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiTrafficSplit()
        with pytest.raises(ValueError, match="100"):
            svc.create_split("inst-1", SplitConfig(split_id="s1", endpoint="/api", targets=[
                TrafficTarget(version="v1", weight=60, upstream="http://v1"),
            ]))

    def test_update_weights(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiTrafficSplit()
        svc.create_split("inst-1", SplitConfig(split_id="s1", endpoint="/api", targets=[
            TrafficTarget(version="v1", weight=90, upstream="http://v1"),
            TrafficTarget(version="v2", weight=10, upstream="http://v2"),
        ]))
        svc.update_weights("inst-1", "/api", {"v1": 50, "v2": 50})
        split = svc.list_splits("inst-1")[0]
        assert split.targets[0].weight == 50

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiTrafficSplit()
        svc.create_split("inst-1", SplitConfig(split_id="s1", endpoint="/api", targets=[TrafficTarget(version="v1", weight=100, upstream="http://v1")]))
        assert len(svc.list_splits("inst-2")) == 0
