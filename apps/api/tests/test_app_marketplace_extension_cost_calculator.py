from app.services.app_marketplace_extension_cost_calculator import CostCalculator


def test_calculate_basic():
    cc = CostCalculator()
    breakdown = cc.calculate(compute_minutes=100, storage_gb=5, bandwidth_gb=2, api_calls=10000)
    assert breakdown.compute_cents == 100
    assert breakdown.storage_cents == 125
    assert breakdown.bandwidth_cents == 20
    assert breakdown.api_calls_cents == 50
    assert breakdown.total_cents == 295


def test_estimate_monthly():
    cc = CostCalculator()
    estimate = cc.estimate_monthly(
        daily_compute_min=10, storage_gb=2,
        daily_bandwidth_gb=0.5, daily_api_calls=5000,
    )
    assert estimate["compute"] == 300      # 10 * 30 * 1
    assert estimate["storage"] == 50       # 2 * 25
    assert estimate["bandwidth"] == 150    # 0.5 * 30 * 10
    assert estimate["api_calls"] == 750    # 5000 * 30 / 1000 * 5
    assert estimate["total_dollars"] == 12.50


def test_record_and_total():
    cc = CostCalculator()
    cc.record("ext-1", cc.calculate(60, 1, 1, 5000))
    cc.record("ext-1", cc.calculate(120, 2, 3, 10000))
    total = cc.get_total("ext-1")
    assert total > 0


def test_average_monthly():
    cc = CostCalculator()
    cc.record("ext-2", cc.calculate(100, 1, 1, 1000))
    cc.record("ext-2", cc.calculate(200, 1, 1, 1000))
    avg = cc.get_average_monthly("ext-2")
    assert avg > 0


def test_compare_costs():
    cc = CostCalculator()
    cc.record("cheap", cc.calculate(10, 1, 0.1, 100))
    cc.record("expensive", cc.calculate(1000, 50, 10, 100000))
    comp = cc.compare_costs("cheap", "expensive")
    assert comp["cheaper"] == "cheap"
    assert comp["difference_cents"] > 0


def test_cost_breakdown():
    cc = CostCalculator()
    cc.record("ext-3", cc.calculate(60, 2, 1, 5000))
    bd = cc.get_cost_breakdown("ext-3")
    assert bd["compute"] == 60
    assert bd["storage"] == 50
    assert bd["total"] == bd["compute"] + bd["storage"] + bd["bandwidth"] + bd["api_calls"]
