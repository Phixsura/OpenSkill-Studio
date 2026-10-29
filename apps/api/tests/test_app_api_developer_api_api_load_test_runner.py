from app.services.app_api_developer_api_api_load_test_runner import AppAPIDeveloperAPIApiLoadTestRunner

class TestLoadTestRunner:
    def test_record_passing(self):
        r = AppAPIDeveloperAPIApiLoadTestRunner()
        t = r.record("inst-1", "t1", "/api/users", 100, 10000, 9990, 10, 45.0, 200.0, 500.0)
        assert t.success_rate == 99.9
        assert t.passed is True

    def test_record_failing(self):
        r = AppAPIDeveloperAPIApiLoadTestRunner()
        t = r.record("inst-1", "t1", "/api/users", 100, 10000, 8000, 2000, 500.0, 2000.0, 100.0)
        assert t.passed is False

    def test_failing_tests(self):
        r = AppAPIDeveloperAPIApiLoadTestRunner()
        r.record("inst-1", "t1", "/a", 10, 1000, 999, 1, 50, 200, 100)
        r.record("inst-1", "t2", "/b", 10, 1000, 500, 500, 50, 200, 50)
        assert len(r.failing_tests("inst-1")) == 1

    def test_isolation(self):
        r = AppAPIDeveloperAPIApiLoadTestRunner()
        r.record("inst-1", "t1", "/a", 10, 1000, 1000, 0, 50, 200, 100)
        assert len(r.all_results("inst-2")) == 0
