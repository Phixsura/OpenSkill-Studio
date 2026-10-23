from app.services.app_marketplace_app_app_version_diff_checker import compare_responses

def test_compatible():
    v1 = {"id": "a1", "name": "App", "status": "active"}
    v2 = {"id": "a1", "name": "App Updated", "status": "active", "version": "2.0"}
    r = compare_responses(v1_response=v1, v2_response=v2)
    assert r["compatible"]
    assert "version" in r["added"]
    assert len(r["removed"]) == 0

def test_breaking():
    v1 = {"id": "a1", "name": "App", "rating": 4.5}
    v2 = {"id": "a1", "name": "App", "rating": "4.5"}  # type changed
    r = compare_responses(v1_response=v1, v2_response=v2)
    assert r["breaking"]
    assert r["modified"][0]["type_changed"]

def test_removed():
    v1 = {"id": "a1", "name": "App", "legacy_field": True}
    v2 = {"id": "a1", "name": "App"}
    r = compare_responses(v1_response=v1, v2_response=v2)
    assert r["breaking"]
    assert "legacy_field" in r["removed"]
