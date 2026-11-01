from app.services.app_marketplace_app_app_developer_guide import build_developer_guide

def test_fresh():
    r = build_developer_guide()
    assert r["total"] == 6
    assert r["completed"] == 0
    assert r["next_section"]["id"] == "quickstart"

def test_partial():
    r = build_developer_guide(completed_sections=["quickstart", "concepts"])
    assert r["completed"] == 2
    assert r["progress_pct"] == 33
    assert r["next_section"]["id"] == "guides"

def test_all():
    all_ids = [s["id"] for s in [{"id": "quickstart"}, {"id": "concepts"}, {"id": "guides"},
                                   {"id": "api"}, {"id": "sdks"}, {"id": "best_practices"}]]
    r = build_developer_guide(completed_sections=all_ids)
    assert r["progress_pct"] == 100
