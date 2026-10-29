from app.services.app_api_developer_api_benchmark import AppAPIDeveloperAPIBenchmark

class TestBenchmark:
    def test_record(self):
        b = AppAPIDeveloperAPIBenchmark()
        r = b.record("inst-1", "b1", "GET /api/users", 5000, 20, 150)
        assert r.rps == 5000

    def test_best_rps(self):
        b = AppAPIDeveloperAPIBenchmark()
        b.record("inst-1", "b1", "/fast", 10000, 10, 50)
        b.record("inst-1", "b2", "/slow", 500, 200, 1500)
        assert b.best_rps("inst-1")[0].endpoint == "/fast"

    def test_slowest(self):
        b = AppAPIDeveloperAPIBenchmark()
        b.record("inst-1", "b1", "/fast", 10000, 10, 50)
        b.record("inst-1", "b2", "/slow", 500, 200, 1500)
        assert b.slowest("inst-1")[0].endpoint == "/slow"

    def test_isolation(self):
        b = AppAPIDeveloperAPIBenchmark()
        b.record("inst-1", "b1", "/api", 1000, 50, 200)
        assert b.list_results("inst-2") == []
