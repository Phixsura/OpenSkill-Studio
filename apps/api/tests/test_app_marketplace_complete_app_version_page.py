from app.services.app_marketplace_complete_app_version_page import build_complete_version_page

def test_page():
    versions = [{"version": "2.0", "status": "published"}, {"version": "1.0", "status": "published"},
                {"version": "3.0-beta", "status": "in_review"}]
    p = build_complete_version_page(app={"id": "a1", "name": "App"}, versions=versions,
                                      current=versions[0], pipeline={"status": "running"})
    assert p["stats"]["published"] == 2
    assert p["stats"]["in_review"] == 1
    assert len(p["actions"]) == 2
