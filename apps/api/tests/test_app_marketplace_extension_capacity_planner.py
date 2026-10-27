from app.services.app_marketplace_extension_capacity_planner import (
    CapacityPlannerService, SystemProfile
)


def test_low_utilization():
    cp = CapacityPlannerService()
    profile = SystemProfile("api", arrival_rate=50, service_rate=200, instances=1)
    report = cp.analyze(profile)
    assert report.utilization == 0.25
    assert report.avg_response_ms < 200
    assert report.meets_sla is True
    assert report.headroom_pct > 0


def test_high_utilization():
    cp = CapacityPlannerService()
    profile = SystemProfile("api", arrival_rate=180, service_rate=200, instances=1)
    report = cp.analyze(profile)
    assert report.utilization == 0.9
    assert report.avg_response_ms > 50  # high latency due to queuing


def test_overloaded():
    cp = CapacityPlannerService()
    profile = SystemProfile("api", arrival_rate=300, service_rate=200, instances=1)
    report = cp.analyze(profile)
    assert report.utilization >= 1.0
    assert report.meets_sla is False


def test_multi_instance():
    cp = CapacityPlannerService()
    profile = SystemProfile("api", arrival_rate=300, service_rate=200, instances=2)
    report = cp.analyze(profile)
    assert report.utilization < 1.0  # 300/400 = 0.75
    assert report.throughput == 300


def test_recommend_instances():
    cp = CapacityPlannerService()
    profile = SystemProfile("api", arrival_rate=500, service_rate=100,
                            instances=3, sla_latency_ms=50)
    rec = cp.recommend_instances(profile, target_utilization=0.7)
    assert rec["recommended_instances"] >= 7  # 500/(100*0.7) ≈ 8
    assert rec["change"] > 0


def test_what_if_double_load():
    cp = CapacityPlannerService()
    profile = SystemProfile("api", arrival_rate=100, service_rate=200, instances=1)
    base = cp.analyze(profile)
    doubled = cp.what_if(profile, 2.0)
    assert doubled.utilization > base.utilization
    assert doubled.avg_response_ms > base.avg_response_ms


def test_littles_law():
    cp = CapacityPlannerService()
    result = cp.littles_law(arrival_rate=10, avg_time_in_system=0.5)
    assert result["avg_items_in_system"] == 5.0  # L = 10 * 0.5


def test_sla_headroom():
    cp = CapacityPlannerService()
    profile = SystemProfile("api", arrival_rate=50, service_rate=200,
                            instances=1, sla_latency_ms=100)
    report = cp.analyze(profile)
    assert report.headroom_pct > 0
    # At higher load, headroom should decrease
    report2 = cp.analyze(SystemProfile("api", 150, 200, 1, 100))
    assert report2.headroom_pct < report.headroom_pct
