from app.services.app_marketplace_app_app_onboarding_checklist import build_onboarding_checklist

def test_checklist():
    tasks = [
        {"id": "1", "title": "Create app", "completed": True, "icon": "🔧"},
        {"id": "2", "title": "Add webhook", "completed": False},
        {"id": "3", "title": "Submit for review", "completed": False, "required": False},
    ]
    r = build_onboarding_checklist(tasks=tasks, user_name="Alice")
    assert r["completed"] == 1
    assert r["total"] == 3
    assert r["progress_pct"] == 33
    assert not r["all_done"]
    assert "Alice" in r["greeting"]

def test_all_done():
    tasks = [{"id": "1", "title": "Done", "completed": True}]
    r = build_onboarding_checklist(tasks=tasks)
    assert r["all_done"]
    assert r["progress_pct"] == 100
