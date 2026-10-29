import pytest
from app.services.app_api_developer_api_api_usage_forecast import AppAPIDeveloperAPIApiUsageForecast

class TestUsageForecast:
    def test_growing(self):
        f = AppAPIDeveloperAPIApiUsageForecast()
        for v in [100, 110, 120, 130, 140, 150]:
            f.add_daily_sample("inst-1", "/api/users", v)
        r = f.forecast("inst-1", "/api/users")
        assert r.trend == "growing"
        assert r.forecast_30d >= r.current_daily_avg

    def test_stable(self):
        f = AppAPIDeveloperAPIApiUsageForecast()
        for v in [100, 101, 99, 100, 101, 100]:
            f.add_daily_sample("inst-1", "/api/data", v)
        r = f.forecast("inst-1", "/api/data")
        assert r.trend == "stable"

    def test_too_few_samples(self):
        f = AppAPIDeveloperAPIApiUsageForecast()
        f.add_daily_sample("inst-1", "/api", 100)
        with pytest.raises(ValueError, match="3 daily"):
            f.forecast("inst-1", "/api")

    def test_growing_endpoints(self):
        f = AppAPIDeveloperAPIApiUsageForecast()
        for v in [100, 200, 300]: f.add_daily_sample("inst-1", "/grow", v)
        for v in [100, 100, 100]: f.add_daily_sample("inst-1", "/flat", v)
        assert len(f.growing_endpoints("inst-1")) == 1

    def test_isolation(self):
        f = AppAPIDeveloperAPIApiUsageForecast()
        for v in [100, 200, 300]: f.add_daily_sample("inst-1", "/api", v)
        assert len(f.all_forecasts("inst-2")) == 0
