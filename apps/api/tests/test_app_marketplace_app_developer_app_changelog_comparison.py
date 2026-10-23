from app.services.app_marketplace_app_developer_app_changelog_comparison import compare_changelogs

def test_compare():
    a = {"version": "1.0", "changes": [{"description": "Feature A"}, {"description": "Fix B"}]}
    b = {"version": "2.0", "changes": [{"description": "Feature A"}, {"description": "Feature C"}]}
    r = compare_changelogs(version_a=a, version_b=b)
    assert r["only_in_a"] == ["Fix B"]
    assert r["only_in_b"] == ["Feature C"]
    assert r["common"] == ["Feature A"]
    assert r["total_unique"] == 3
