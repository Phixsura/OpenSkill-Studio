from app.services.app_marketplace_app_developer_api_changelog import build_api_changelog, compute_api_stability

def test_changelog():
    versions = [{"version": "2.0", "endpoints_added": ["/new"], "endpoints_removed": ["/old"], "endpoints_modified": []},
                {"version": "1.1", "endpoints_added": ["/extra"], "endpoints_removed": [], "endpoints_modified": []}]
    c = build_api_changelog(versions=versions)
    assert len(c) == 2
    assert c[0]["breaking"]
    assert not c[1]["breaking"]

def test_stability():
    changelog = [{"breaking": True}, {"breaking": False}, {"breaking": True}]
    s = compute_api_stability(changelog=changelog)
    assert s["stability_score"] == 70
    assert s["breaking_changes"] == 2
