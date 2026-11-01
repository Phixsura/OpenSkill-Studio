from app.services.app_marketplace_app_app_app_app_app_app_app_svc_blueprint import create_blueprint, validate_blueprint

def test_create():
    r = create_blueprint("api-stack", [
        {"name": "api", "type": "service", "estimated_cost": 500},
        {"name": "db", "type": "database", "estimated_cost": 300},
        {"name": "cache", "type": "cache", "estimated_cost": 100},
    ])
    assert r["component_count"] == 3
    assert r["estimated_monthly_cost"] == 900

def test_validate():
    bp = create_blueprint("minimal", [{"name": "api", "type": "service"}])
    r = validate_blueprint(bp)
    assert not r["valid"]
    assert r["issue_count"] >= 1
