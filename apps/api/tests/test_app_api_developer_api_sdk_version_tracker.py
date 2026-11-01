from app.services.app_api_developer_api_sdk_version_tracker import AppAPIDeveloperAPISDKVersionTracker

class TestSDKVersionTracker:
    def test_track(self):
        t = AppAPIDeveloperAPISDKVersionTracker()
        v = t.track("inst-1", "c1", "openskill-sdk", "1.2.0", "python")
        assert v.request_count == 1

    def test_by_version(self):
        t = AppAPIDeveloperAPISDKVersionTracker()
        t.track("inst-1", "c1", "sdk", "1.0", "python")
        t.track("inst-1", "c2", "sdk", "1.0", "python")
        t.track("inst-1", "c3", "sdk", "2.0", "node")
        assert t.by_version("inst-1") == {"1.0": 2, "2.0": 1}

    def test_outdated(self):
        t = AppAPIDeveloperAPISDKVersionTracker()
        t.track("inst-1", "c1", "sdk", "1.0", "python")
        t.track("inst-1", "c2", "sdk", "2.0", "python")
        assert len(t.outdated("inst-1", "2.0")) == 1

    def test_by_language(self):
        t = AppAPIDeveloperAPISDKVersionTracker()
        t.track("inst-1", "c1", "sdk", "1.0", "python")
        t.track("inst-1", "c2", "sdk", "1.0", "node")
        assert t.by_language("inst-1") == {"python": 1, "node": 1}

    def test_isolation(self):
        t = AppAPIDeveloperAPISDKVersionTracker()
        t.track("inst-1", "c1", "sdk", "1.0", "python")
        assert len(t.outdated("inst-2", "1.0")) == 0
