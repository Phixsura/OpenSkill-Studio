from app.services.app_marketplace_app_app_app_app_app_app_app_changelog_sub import ChangelogSubscriber

def test_subscribe():
    cs = ChangelogSubscriber()
    cs.subscribe(email="a@b.com", categories=["releases"], frequency="daily")
    cs.subscribe(email="c@d.com")
    assert len(cs.list_active()) == 2
    assert len(cs.list_active(category="releases")) == 2  # "all" + "releases"
    cs.unsubscribe("a@b.com")
    assert cs.stats()["active"] == 1
