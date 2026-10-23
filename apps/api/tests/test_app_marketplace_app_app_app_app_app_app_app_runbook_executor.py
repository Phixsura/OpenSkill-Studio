from app.services.app_marketplace_app_app_app_app_app_app_app_runbook_executor import create_runbook, execute_step

def test_runbook():
    rb = create_runbook(name="Deploy Checklist", steps=[
        {"title": "Check health", "command": "curl /health"},
        {"title": "Run migrations", "command": "alembic upgrade head"},
        {"title": "Restart service", "command": "systemctl restart app"},
    ], tags=["deploy"])
    assert rb["status"] == "ready"
    assert rb["total_steps"] == 3
    execute_step(rb, 0, output="OK", success=True)
    execute_step(rb, 1, output="Applied 2 migrations", success=True)
    r = execute_step(rb, 2, output="Restarted", success=True)
    assert r["runbook_status"] == "completed"
    assert r["progress"] == "3/3"

def test_failure():
    rb = create_runbook(name="Test", steps=[{"title": "Step 1"}, {"title": "Step 2"}])
    execute_step(rb, 0, output="error", success=False)
    assert rb["status"] == "failed"
