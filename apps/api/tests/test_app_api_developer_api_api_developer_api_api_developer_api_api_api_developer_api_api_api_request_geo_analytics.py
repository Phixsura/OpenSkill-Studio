import pytest
from app.services.app_api_developer_api_api_developer_api_api_developer_api_api_api_developer_api_api_api_request_geo_analytics import AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiDeveloperApiApiApiRequestGeoAnalytics

class TestGeoAnalytics:
    def test_record(self):
        g = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiDeveloperApiApiApiRequestGeoAnalytics()
        r = g.record("inst-1", "NA", 5000, 45.0)
        assert r.request_count == 5000

    def test_invalid_region(self):
        g = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiDeveloperApiApiApiRequestGeoAnalytics()
        with pytest.raises(ValueError):
            g.record("inst-1", "MARS", 100, 50)

    def test_distribution(self):
        g = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiDeveloperApiApiApiRequestGeoAnalytics()
        g.record("inst-1", "NA", 5000, 45)
        g.record("inst-1", "EU", 3000, 60)
        g.record("inst-1", "APAC", 2000, 120)
        dist = g.distribution("inst-1")
        assert dist[0].region == "NA"

    def test_slowest(self):
        g = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiDeveloperApiApiApiRequestGeoAnalytics()
        g.record("inst-1", "NA", 5000, 45)
        g.record("inst-1", "APAC", 2000, 200)
        assert g.slowest_region("inst-1").region == "APAC"

    def test_isolation(self):
        g = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiDeveloperApiApiApiRequestGeoAnalytics()
        g.record("inst-1", "NA", 1000, 50)
        assert g.total_requests("inst-2") == 0
