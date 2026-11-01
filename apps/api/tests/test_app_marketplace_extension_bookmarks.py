from app.services.app_marketplace_extension_bookmarks import ExtensionBookmarksService


def test_add_and_get():
    svc = ExtensionBookmarksService()
    svc.add("user-1", "ext-slack", note="Great tool", tags=["comm"])
    bms = svc.get_all("user-1")
    assert len(bms) == 1
    assert bms[0].note == "Great tool"


def test_no_duplicate():
    svc = ExtensionBookmarksService()
    svc.add("user-1", "ext-1")
    svc.add("user-1", "ext-1")
    assert svc.get_count("user-1") == 1


def test_remove():
    svc = ExtensionBookmarksService()
    svc.add("user-1", "ext-1")
    assert svc.remove("user-1", "ext-1") is True
    assert svc.is_bookmarked("user-1", "ext-1") is False


def test_collections():
    svc = ExtensionBookmarksService()
    svc.add("user-1", "ext-1", collection="tools")
    svc.add("user-1", "ext-2", collection="analytics")
    svc.add("user-1", "ext-3", collection="tools")
    assert svc.get_collections("user-1") == ["analytics", "tools"]
    assert len(svc.get_all("user-1", collection="tools")) == 2


def test_search():
    svc = ExtensionBookmarksService()
    svc.add("user-1", "ext-slack", tags=["messaging"])
    svc.add("user-1", "ext-github", tags=["dev"])
    results = svc.search("user-1", "messag")
    assert len(results) == 1
