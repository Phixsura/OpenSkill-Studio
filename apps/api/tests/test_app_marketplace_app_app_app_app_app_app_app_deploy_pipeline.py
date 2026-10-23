from app.services.app_marketplace_app_app_app_app_app_app_app_deploy_pipeline import create_pipeline, execute_pipeline

def test_pipeline():
    p = create_pipeline(name="Production", stages=[
        {"name": "Build", "type": "build"},
        {"name": "Test", "type": "test"},
        {"name": "Staging", "type": "deploy", "environment": "staging"},
        {"name": "Approval", "type": "gate", "approval_required": True},
        {"name": "Production", "type": "deploy", "environment": "production"},
    ])
    assert p["total_stages"] == 5
    assert p["has_approval_gates"]
    r = execute_pipeline(p)
    assert r["completed"] == 3  # Build, Test, Staging done, blocked at Approval
    assert r["blocked"]
    assert r["progress_pct"] == 60
