from app.services.app_marketplace_app_marketplace_developer_app_onboarding_checklist_v2 import get_checklist_progress

def test_empty():
    r = get_checklist_progress(completed=[])
    assert r["pct"] == 0
    assert r["next_item"]["id"] == "create_account"

def test_partial():
    r = get_checklist_progress(completed=["create_account", "complete_profile"])
    assert r["completed_count"] == 2
    assert r["points_earned"] == 25

def test_all():
    all_ids = [i["id"] for i in [{"id": "create_account"}, {"id": "complete_profile"}, {"id": "read_docs"},
               {"id": "create_app"}, {"id": "add_manifest"}, {"id": "run_tests"},
               {"id": "submit_review"}, {"id": "get_published"}, {"id": "first_install"}, {"id": "first_review"}]]
    r = get_checklist_progress(completed=all_ids)
    assert r["pct"] == 100
    assert r["next_item"] is None
