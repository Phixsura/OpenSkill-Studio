from app.services.app_marketplace_extension_favorites import ExtensionFavoritesService


def test_add_and_list():
    svc = ExtensionFavoritesService()
    svc.add("u1", "ext-1")
    svc.add("u1", "ext-2")
    assert svc.get_count("u1") == 2
    assert svc.is_favorite("u1", "ext-1") is True


def test_remove():
    svc = ExtensionFavoritesService()
    svc.add("u1", "ext-1")
    svc.remove("u1", "ext-1")
    assert svc.is_favorite("u1", "ext-1") is False


def test_pin_ordering():
    svc = ExtensionFavoritesService()
    svc.add("u1", "ext-1")
    svc.add("u1", "ext-2")
    svc.toggle_pin("u1", "ext-2")
    favs = svc.get_favorites("u1")
    assert favs[0].extension_id == "ext-2"  # pinned first


def test_access_tracking():
    svc = ExtensionFavoritesService()
    svc.add("u1", "ext-1")
    svc.access("u1", "ext-1")
    svc.access("u1", "ext-1")
    favs = svc.get_favorites("u1")
    assert favs[0].access_count == 2


def test_no_duplicate():
    svc = ExtensionFavoritesService()
    svc.add("u1", "ext-1")
    result = svc.add("u1", "ext-1")
    assert svc.get_count("u1") == 1
