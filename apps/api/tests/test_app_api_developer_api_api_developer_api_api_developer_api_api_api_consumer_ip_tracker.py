from app.services.app_api_developer_api_api_developer_api_api_developer_api_api_api_consumer_ip_tracker import AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiConsumerIpTracker

class TestConsumerIpTracker:
    def test_track(self):
        t = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiConsumerIpTracker()
        r = t.track("inst-1", "c1", "1.2.3.4")
        assert r.unique_ip_count == 1

    def test_multiple_ips(self):
        t = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiConsumerIpTracker()
        t.track("inst-1", "c1", "1.1.1.1")
        t.track("inst-1", "c1", "2.2.2.2")
        t.track("inst-1", "c1", "1.1.1.1")
        r = t.get("inst-1", "c1")
        assert r.unique_ip_count == 2
        assert r.total_requests == 3
        assert r.top_ip == "1.1.1.1"

    def test_suspicious(self):
        t = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiConsumerIpTracker()
        for i in range(15): t.track("inst-1", "c1", f"10.0.0.{i}")
        t.track("inst-1", "c2", "10.0.0.1")
        assert len(t.suspicious_consumers("inst-1", max_ips=10)) == 1

    def test_isolation(self):
        t = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiConsumerIpTracker()
        t.track("inst-1", "c1", "1.1.1.1")
        assert len(t.all_records("inst-2")) == 0
