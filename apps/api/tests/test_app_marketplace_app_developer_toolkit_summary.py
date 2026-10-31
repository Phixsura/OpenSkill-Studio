from app.services.app_marketplace_app_developer_toolkit_summary import get_toolkit_summary, get_tools_by_category

def test_summary():
    s = get_toolkit_summary()
    assert s["total_tools"] == 12
    assert len(s["categories"]) == 4

def test_build():
    t = get_tools_by_category(category="build")
    assert len(t) == 3
    assert any(x["name"] == "SDK" for x in t)

def test_unknown():
    assert get_tools_by_category(category="magic") == []
