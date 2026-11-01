from app.services.app_api_developer_api_ip_geolocation_tracker import AppAPIDeveloperAPIIPGeolocationTracker

class TestGeoTracker:
    def test_track(self):
        t = AppAPIDeveloperAPIIPGeolocationTracker()
        g = t.track("inst-1", "1.2.3.4", "US", "California")
        assert g.request_count == 1
        assert len(g.unique_ips) == 1

    def test_top_countries(self):
        t = AppAPIDeveloperAPIIPGeolocationTracker()
        for _ in range(10): t.track("inst-1", "1.1.1.1", "US")
        for _ in range(5): t.track("inst-1", "2.2.2.2", "DE")
        top = t.top_countries("inst-1", 1)
        assert top[0].country == "US"

    def test_unique_ips(self):
        t = AppAPIDeveloperAPIIPGeolocationTracker()
        t.track("inst-1", "1.1.1.1", "US")
        t.track("inst-1", "1.1.1.1", "US")
        t.track("inst-1", "2.2.2.2", "US")
        assert t.total_unique_ips("inst-1") == 2

    def test_error_count(self):
        t = AppAPIDeveloperAPIIPGeolocationTracker()
        t.track("inst-1", "1.1.1.1", "US", success=False)
        assert t.top_countries("inst-1")[0].error_count == 1

    def test_isolation(self):
        t = AppAPIDeveloperAPIIPGeolocationTracker()
        t.track("inst-1", "1.1.1.1", "US")
        assert t.total_countries("inst-2") == 0
