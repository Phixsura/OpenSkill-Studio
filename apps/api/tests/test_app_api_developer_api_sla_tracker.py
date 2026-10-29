from app.services.app_api_developer_api_sla_tracker import AppAPIDeveloperAPISLATracker

class TestSLA:
    def test_met(self):
        s = AppAPIDeveloperAPISLATracker()
        s.set_target("inst-1", "API", 99.9, 200)
        s.update_actuals("inst-1", "API", 99.95, 150)
        assert s.list_slas("inst-1")[0].sla_met is True

    def test_violated(self):
        s = AppAPIDeveloperAPISLATracker()
        s.set_target("inst-1", "API", 99.9, 200)
        s.update_actuals("inst-1", "API", 99.5, 300)
        assert len(s.violations("inst-1")) == 1

    def test_partial(self):
        s = AppAPIDeveloperAPISLATracker()
        s.set_target("inst-1", "API", 99.9, 200)
        s.update_actuals("inst-1", "API", 99.95, 300)  # latency violated
        sla = s.list_slas("inst-1")[0]
        assert sla.uptime_met is True
        assert sla.latency_met is False
        assert sla.sla_met is False

    def test_isolation(self):
        s = AppAPIDeveloperAPISLATracker()
        s.set_target("inst-1", "API", 99.9, 200)
        assert s.list_slas("inst-2") == []
