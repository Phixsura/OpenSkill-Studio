from app.services.app_marketplace_app_app_migration_planner import build_migration_plan

def test_plan():
    steps = [
        {"name": "Add column", "type": "schema", "risk": "low", "estimated_seconds": 5, "reversible": True},
        {"name": "Backfill data", "type": "data", "risk": "medium", "estimated_seconds": 120, "reversible": False},
        {"name": "Drop old column", "type": "schema", "risk": "high", "estimated_seconds": 2, "reversible": False},
    ]
    r = build_migration_plan(steps=steps)
    assert r["total_steps"] == 3
    assert r["total_estimated_seconds"] == 127
    assert r["has_irreversible"]
    assert r["steps"][0]["order"] == 1

def test_empty():
    r = build_migration_plan(steps=[])
    assert r["total_steps"] == 0
    assert not r["has_irreversible"]
