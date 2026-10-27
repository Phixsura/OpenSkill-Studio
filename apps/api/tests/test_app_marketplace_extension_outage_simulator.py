from app.services.app_marketplace_extension_outage_simulator import OutageSimulatorService


def test_direct_failure():
    sim = OutageSimulatorService()
    sim.register_component("api")
    sim.register_component("db")
    sim.define_scenario("s1", "DB Outage", "Database goes down",
                        affected=["db"], cascading=False)
    result = sim.simulate("s1")
    assert result.total_affected == 1
    assert result.status == "completed"


def test_cascading_failure():
    sim = OutageSimulatorService()
    sim.register_component("storage")
    sim.register_component("db", ["storage"])
    sim.register_component("api", ["db"])
    sim.register_component("frontend", ["api"])
    sim.define_scenario("s1", "Storage Failure", "Storage dies",
                        affected=["storage"])
    result = sim.simulate("s1")
    # storage → db → api → frontend all affected
    assert result.total_affected == 4


def test_partial_cascade():
    sim = OutageSimulatorService()
    sim.register_component("db")
    sim.register_component("cache")
    sim.register_component("api", ["db", "cache"])
    sim.register_component("worker", ["db"])
    sim.register_component("static")  # no deps, unaffected
    sim.define_scenario("s1", "Cache Down", "Cache failure",
                        affected=["cache"])
    result = sim.simulate("s1")
    assert result.total_affected == 2  # cache + api (depends on cache)


def test_no_cascade_when_disabled():
    sim = OutageSimulatorService()
    sim.register_component("db")
    sim.register_component("api", ["db"])
    sim.define_scenario("s1", "DB Down", "DB", affected=["db"], cascading=False)
    result = sim.simulate("s1")
    assert result.total_affected == 1  # only db, no cascade


def test_postmortem():
    sim = OutageSimulatorService()
    sim.register_component("storage")
    sim.register_component("db", ["storage"])
    sim.register_component("api", ["db"])
    sim.define_scenario("s1", "Storage Outage", "Storage failure",
                        affected=["storage"])
    result = sim.simulate("s1")
    report = sim.generate_postmortem(result)
    assert report["direct_failures"] == 1
    assert report["cascading_failures"] == 2
    assert report["blast_radius_pct"] == 100.0
    assert len(report["recommendations"]) > 0


def test_blast_radius():
    sim = OutageSimulatorService()
    for i in range(10):
        sim.register_component(f"svc-{i}")
    sim.register_component("critical", [])
    sim.register_component("dependent", ["critical"])
    sim.define_scenario("s1", "Critical Down", "test",
                        affected=["critical"])
    result = sim.simulate("s1")
    report = sim.generate_postmortem(result)
    assert report["blast_radius_pct"] < 50  # only 2/12 affected


def test_mttr_tracked():
    sim = OutageSimulatorService()
    sim.register_component("api")
    sim.define_scenario("s1", "API Down", "test", affected=["api"])
    result = sim.simulate("s1")
    assert result.mttr_seconds >= 0
    assert result.recovered_at > result.started_at


def test_recovery_events():
    sim = OutageSimulatorService()
    sim.register_component("db")
    sim.register_component("api", ["db"])
    sim.define_scenario("s1", "DB Down", "test", affected=["db"])
    result = sim.simulate("s1")
    recovered = [e for e in result.events if e.event_type == "recovered"]
    assert len(recovered) == 2  # db and api both recovered
