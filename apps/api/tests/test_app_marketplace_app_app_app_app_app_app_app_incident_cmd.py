from app.services.app_marketplace_app_app_app_app_app_app_app_incident_cmd import IncidentCommander
def test_lifecycle():
    ic = IncidentCommander()
    ic.declare("inc-1", "critical", "alice", "API Down")
    ic.add_action("inc-1", "Restart pods", "bob")
    assert len(ic.active()) == 1
    ic.resolve("inc-1")
    assert len(ic.active()) == 0
