from app.services.app_api_developer_api_api_developer_api_api_developer_api_integration_test_runner import AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiIntegrationTestRunner

class TestIntegrationTestRunner:
    def test_start_run(self):
        r = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiIntegrationTestRunner()
        run = r.start_run("inst-1", "r1", "API Suite")
        assert run.total == 0

    def test_add_results(self):
        r = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiIntegrationTestRunner()
        r.start_run("inst-1", "r1", "Suite")
        r.add_result("inst-1", "r1", "test_login", "passed", 50)
        r.add_result("inst-1", "r1", "test_signup", "failed", 100, "Timeout")
        run = r.recent_runs("inst-1")[0]
        assert run.total == 2
        assert run.pass_rate == 50.0

    def test_all_passed(self):
        r = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiIntegrationTestRunner()
        r.start_run("inst-1", "r1", "Suite")
        r.add_result("inst-1", "r1", "test_a", "passed", 50)
        r.add_result("inst-1", "r1", "test_b", "passed", 30)
        assert r.recent_runs("inst-1")[0].all_passed is True

    def test_failing_runs(self):
        r = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiIntegrationTestRunner()
        r.start_run("inst-1", "r1", "Good")
        r.add_result("inst-1", "r1", "t", "passed")
        r.start_run("inst-1", "r2", "Bad")
        r.add_result("inst-1", "r2", "t", "failed")
        assert len(r.failing_runs("inst-1")) == 1

    def test_isolation(self):
        r = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiIntegrationTestRunner()
        r.start_run("inst-1", "r1", "Suite")
        assert len(r.recent_runs("inst-2")) == 0
