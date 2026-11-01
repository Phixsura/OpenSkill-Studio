from app.services.app_marketplace_app_app_app_app_app_app_app_deploy_impact import analyze_impact, should_require_approval

def test_high_impact():
    r = analyze_impact(
        {"services": ["api", "db", "cache", "worker"], "has_db_migration": True,
         "breaking_changes": True, "env": "production"},
        {"total_services": 10, "service_users": {"api": 5000, "db": 0, "cache": 0, "worker": 0}})
    assert r["risk"] == "high"
    assert r["users_affected"] == 5000
    assert "database_migration" in r["risk_factors"]

def test_low_impact():
    r = analyze_impact(
        {"services": ["docs"], "env": "staging"},
        {"total_services": 10, "service_users": {"docs": 100}})
    assert r["risk"] == "low"

def test_approval():
    impact = {"risk": "high", "impact_pct": 40}
    r = should_require_approval(impact)
    assert r["require_approval"]
