from app.services.app_marketplace_extension_benchmark_runner import ExtBenchmarkRunnerService

def test_run():
    svc = ExtBenchmarkRunnerService()
    r = svc.run("ext-1", "render", [10, 12, 11, 15, 9, 8, 20, 13])
    assert r.mean_ms > 0
    assert r.p95_ms >= r.mean_ms

def test_compare():
    svc = ExtBenchmarkRunnerService()
    svc.run("ext-1", "render", [10, 12, 11])
    svc.run("ext-2", "render", [20, 22, 21])
    cmp = svc.compare("ext-1", "ext-2", "render")
    assert cmp["faster"] == "ext-1"

def test_no_samples():
    svc = ExtBenchmarkRunnerService()
    try:
        svc.run("ext-1", "render", [])
        assert False
    except ValueError:
        pass
