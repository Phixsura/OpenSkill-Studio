from app.services.app_marketplace_app_app_app_app_app_app_app_card_actions import get_card_actions, get_quick_actions

def test_not_installed():
    r = get_card_actions(installed=False, owned=False, favorited=False)
    assert r[0]["id"] == "install"
    assert any(a["id"] == "favorite" for a in r)

def test_installed_owned():
    r = get_card_actions(installed=True, owned=True, favorited=True)
    assert r[0]["id"] == "open"
    assert any(a["id"] == "edit" for a in r)
    assert any(a["label"] == "Unfavorite" for a in r)

def test_quick():
    assert get_quick_actions("draft")[0]["id"] == "publish"
    assert get_quick_actions("published")[0]["id"] == "update"
    assert len(get_quick_actions("suspended")) == 0
