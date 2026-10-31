import pytest
from app.services.app_api_developer_api_api_usage_heatmap import AppAPIDeveloperAPIApiUsageHeatmap

class TestUsageHeatmap:
    def test_record(self):
        h = AppAPIDeveloperAPIApiUsageHeatmap()
        b = h.record("inst-1", 0, 9)
        assert b.request_count == 1

    def test_accumulate(self):
        h = AppAPIDeveloperAPIApiUsageHeatmap()
        for _ in range(10): h.record("inst-1", 0, 9)
        assert h.heatmap("inst-1")[0].request_count == 10

    def test_peak_hour(self):
        h = AppAPIDeveloperAPIApiUsageHeatmap()
        for _ in range(5): h.record("inst-1", 0, 9)
        for _ in range(10): h.record("inst-1", 1, 14)
        peak = h.peak_hour("inst-1")
        assert peak.hour == 14

    def test_invalid_day(self):
        h = AppAPIDeveloperAPIApiUsageHeatmap()
        with pytest.raises(ValueError):
            h.record("inst-1", 7, 0)

    def test_isolation(self):
        h = AppAPIDeveloperAPIApiUsageHeatmap()
        h.record("inst-1", 0, 9)
        assert h.total_requests("inst-2") == 0
