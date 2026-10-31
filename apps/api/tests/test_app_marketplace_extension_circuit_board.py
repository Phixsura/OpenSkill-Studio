from app.services.app_marketplace_extension_circuit_board import CircuitBoardService


def test_register():
    cb = CircuitBoardService()
    cb.register("api", ["db", "cache"], critical=True)
    cb.register("db", redundancy=2)
    cb.register("cache")
    assert len(cb.get_board()) == 3


def test_cascade_impact():
    cb = CircuitBoardService()
    cb.register("storage")
    cb.register("db", ["storage"])
    cb.register("api", ["db", "cache"], critical=True)
    cb.register("cache")
    cb.register("frontend", ["api"])
    impact = cb.cascade_impact("storage")
    assert "db" in impact["impacted_services"]
    assert "api" in impact["impacted_services"]
    assert "frontend" in impact["impacted_services"]
    assert "cache" not in impact["impacted_services"]
    assert "api" in impact["critical_impacted"]


def test_blast_radius():
    cb = CircuitBoardService()
    cb.register("core")
    cb.register("a", ["core"])
    cb.register("b", ["core"])
    cb.register("c", ["core"])
    cb.register("independent")
    impact = cb.cascade_impact("core")
    assert impact["blast_radius_pct"] == 60.0  # 3/5


def test_critical_paths():
    cb = CircuitBoardService()
    cb.register("db", redundancy=1)
    cb.register("cache", redundancy=3)
    cb.register("api", ["db", "cache"])
    spofs = cb.find_critical_paths()
    assert "db" in spofs  # single instance, has dependents
    assert "cache" not in spofs  # 3 replicas


def test_recovery_order():
    cb = CircuitBoardService()
    cb.register("db")
    cb.register("cache")
    cb.register("api", ["db", "cache"])
    cb.register("frontend", ["api"])
    order = cb.recovery_order()
    # db and cache first (no deps), then api, then frontend
    assert set(order[0]) == {"db", "cache"}
    assert order[1] == ["api"]
    assert order[2] == ["frontend"]


def test_readiness_all_healthy():
    cb = CircuitBoardService()
    cb.register("api", critical=True)
    cb.register("db")
    score = cb.readiness_score()
    assert score["score"] == 100.0
    assert score["status"] == "operational"


def test_readiness_degraded():
    cb = CircuitBoardService()
    cb.register("api", critical=True)
    cb.register("db")
    cb.set_status("db", "down")
    score = cb.readiness_score()
    assert score["score"] < 100
    assert score["status"] in ("degraded", "outage")


def test_readiness_critical_weight():
    cb = CircuitBoardService()
    cb.register("critical_svc", critical=True)
    cb.register("minor_svc")
    cb.set_status("critical_svc", "down")
    score1 = cb.readiness_score()
    cb2 = CircuitBoardService()
    cb2.register("critical_svc", critical=True)
    cb2.register("minor_svc")
    cb2.set_status("minor_svc", "down")
    score2 = cb2.readiness_score()
    assert score1["score"] < score2["score"]  # critical down hurts more
