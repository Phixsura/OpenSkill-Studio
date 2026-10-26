from app.services.app_marketplace_extension_usage_forecast import (
    UsageForecastService, UsageSample,
)


def test_trend_growing():
    fs = UsageForecastService()
    for i, val in enumerate([100, 120, 140, 160, 180, 200]):
        fs.add_sample("ext-1", "api_calls", UsageSample(f"day-{i}", val))
    trend = fs.get_trend("ext-1", "api_calls")
    assert trend["direction"] == "growing"
    assert trend["growth_rate"] > 0


def test_trend_stable():
    fs = UsageForecastService()
    for i in range(6):
        fs.add_sample("ext-2", "storage", UsageSample(f"day-{i}", 100))
    trend = fs.get_trend("ext-2", "storage")
    assert trend["direction"] == "stable"


def test_forecast():
    fs = UsageForecastService()
    for i, val in enumerate([10, 20, 30, 40, 50]):
        fs.add_sample("ext-3", "compute", UsageSample(f"d{i}", val))
    forecasts = fs.forecast("ext-3", "compute", 3)
    assert len(forecasts) == 3
    assert forecasts[0]["predicted"] > 50  # should continue upward
    assert forecasts[0]["confidence"] > forecasts[2]["confidence"]


def test_estimate_cost():
    fs = UsageForecastService()
    for i, val in enumerate([1000, 1100, 1200, 1300, 1400]):
        fs.add_sample("ext-4", "api_calls", UsageSample(f"d{i}", val))
    cost = fs.estimate_cost("ext-4", 0.005, "api_calls", 7)
    assert cost["estimated_cost"] > 0
    assert cost["periods"] == 7


def test_anomaly_spike():
    fs = UsageForecastService()
    for i in range(10):
        fs.add_sample("ext-5", "cpu", UsageSample(f"d{i}", 50))
    fs.add_sample("ext-5", "cpu", UsageSample("d10", 500))  # spike!
    result = fs.detect_anomaly("ext-5", "cpu")
    assert result["anomaly"] is True
    assert result["direction"] == "spike"


def test_anomaly_normal():
    fs = UsageForecastService()
    for i in range(10):
        fs.add_sample("ext-6", "mem", UsageSample(f"d{i}", 100 + i))
    fs.add_sample("ext-6", "mem", UsageSample("d10", 110))
    result = fs.detect_anomaly("ext-6", "mem")
    assert result["anomaly"] is False


def test_insufficient_data():
    fs = UsageForecastService()
    fs.add_sample("ext-7", "x", UsageSample("d0", 100))
    assert fs.get_trend("ext-7", "x")["direction"] == "insufficient_data"
    assert fs.forecast("ext-7", "x") == []
