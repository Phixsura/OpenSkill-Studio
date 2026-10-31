from app.services.app_api_developer_api_key_dashboard import AppAPIDeveloperAPIKeyDashboard

class TestDashboard:
    def test_update(self):
        d = AppAPIDeveloperAPIKeyDashboard()
        dash = d.update("inst-1", total_keys=50, active_keys=40, expired_keys=8, revoked_keys=2)
        assert dash.active_keys == 40

    def test_default(self):
        d = AppAPIDeveloperAPIKeyDashboard()
        assert d.get("inst-1").total_keys == 0

    def test_isolation(self):
        d = AppAPIDeveloperAPIKeyDashboard()
        d.update("inst-1", total_keys=10)
        assert d.get("inst-2").total_keys == 0
