from app.services.app_marketplace_extension_tag_manager import ExtensionTagManagerService

def test_add_and_get():
    svc = ExtensionTagManagerService()
    svc.add_tags("ext-1", ["api", "slack", "bot"])
    assert svc.get_tags("ext-1") == ["api", "bot", "slack"]

def test_find_by_tag():
    svc = ExtensionTagManagerService()
    svc.add_tags("ext-1", ["api"])
    svc.add_tags("ext-2", ["api", "ui"])
    assert len(svc.find_by_tag("api")) == 2

def test_popular():
    svc = ExtensionTagManagerService()
    svc.add_tags("e1", ["api"]); svc.add_tags("e2", ["api", "ui"]); svc.add_tags("e3", ["api"])
    popular = svc.get_popular_tags(1)
    assert popular[0] == ("api", 3)
