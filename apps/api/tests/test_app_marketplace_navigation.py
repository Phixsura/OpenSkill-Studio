from app.services.app_marketplace_navigation import get_main_nav, get_developer_nav, get_mobile_nav

def test_main():
    n = get_main_nav(active_id="explore")
    assert n[0]["active"]
    assert not n[1]["active"]
    assert len(n) == 4

def test_dev_nav():
    n = get_developer_nav(active_id="apps", app_count=5)
    apps = next(i for i in n if i["id"] == "apps")
    assert apps["active"]
    assert apps["badge"] == "5"

def test_mobile():
    n = get_mobile_nav(is_developer=True, active_id=None)
    assert any(i["id"] == "developer" for i in n)

def test_mobile_non_dev():
    n = get_mobile_nav(is_developer=False)
    assert not any(i["id"] == "developer" for i in n)
