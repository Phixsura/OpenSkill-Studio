from app.services.app_marketplace_app_disaster_recovery import create_dr_plan, simulate_failover, get_dr_readiness

def test_create():
    p = create_dr_plan(app_id="a1", rpo_minutes=15, rto_minutes=30, backup_regions=["us-west", "eu-west"])
    assert p["status"] == "active"

def test_within_rpo():
    r = simulate_failover(primary_region="us-east", backup_region="us-west", data_lag_minutes=5, rpo_minutes=15)
    assert r["within_rpo"]

def test_exceeds_rpo():
    r = simulate_failover(primary_region="us-east", backup_region="eu-west", data_lag_minutes=30, rpo_minutes=15)
    assert not r["within_rpo"]

def test_ready():
    r = get_dr_readiness(backups_current=True, failover_tested=True, monitoring_active=True)
    assert r["ready"]

def test_not_ready():
    r = get_dr_readiness(backups_current=True, failover_tested=False, monitoring_active=True)
    assert not r["ready"]
    assert r["score"] == "2/3"
