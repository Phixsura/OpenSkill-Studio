from app.services.app_api_developer_api_api_developer_api_api_platform_operational_readiness import AppAPIDeveloperAPIApiDeveloperApiApiPlatformOperationalReadiness

class TestOperationalReadiness:
    def test_add_check(self):
        r = AppAPIDeveloperAPIApiDeveloperApiApiPlatformOperationalReadiness()
        report = r.add_check("inst-1", "c1", "security", "HTTPS enforced")
        assert report.total == 1

    def test_go(self):
        r = AppAPIDeveloperAPIApiDeveloperApiApiPlatformOperationalReadiness()
        r.add_check("inst-1", "c1", "security", "HTTPS")
        r.add_check("inst-1", "c2", "monitoring", "Alerts")
        r.pass_check("inst-1", "c1")
        r.pass_check("inst-1", "c2")
        assert r.get_report("inst-1").go_no_go == "GO"

    def test_no_go(self):
        r = AppAPIDeveloperAPIApiDeveloperApiApiPlatformOperationalReadiness()
        r.add_check("inst-1", "c1", "security", "HTTPS", required=True)
        assert r.get_report("inst-1").go_no_go == "NO_GO"

    def test_go_with_caveats(self):
        r = AppAPIDeveloperAPIApiDeveloperApiApiPlatformOperationalReadiness()
        r.add_check("inst-1", "c1", "security", "HTTPS", required=True)
        r.add_check("inst-1", "c2", "documentation", "Docs", required=False)
        r.pass_check("inst-1", "c1")
        report = r.get_report("inst-1")
        assert report.go_no_go == "GO_WITH_CAVEATS"

    def test_isolation(self):
        r = AppAPIDeveloperAPIApiDeveloperApiApiPlatformOperationalReadiness()
        r.add_check("inst-1", "c1", "security", "X")
        assert r.get_report("inst-2").total == 0
