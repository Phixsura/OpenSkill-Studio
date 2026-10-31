from app.services.app_marketplace_extension_marketplace_home import MarketplaceHomeService


def test_add_sections():
    svc = MarketplaceHomeService()
    svc.add_section("trending", "Trending", "trending",
                    [{"id": "ext-1", "name": "Slack Bot"}], order=1)
    svc.add_section("new", "New Arrivals", "new",
                    [{"id": "ext-2", "name": "GitHub Sync"}], order=2)
    homepage = svc.get_homepage()
    assert len(homepage["sections"]) == 2
    assert homepage["sections"][0]["title"] == "Trending"


def test_featured():
    svc = MarketplaceHomeService()
    svc.set_featured([{"id": "ext-1", "name": "Top Pick"}])
    homepage = svc.get_homepage()
    assert len(homepage["featured"]) == 1


def test_reorder():
    svc = MarketplaceHomeService()
    svc.add_section("a", "A", "new", [], order=1)
    svc.add_section("b", "B", "trending", [], order=2)
    svc.reorder(["b", "a"])
    homepage = svc.get_homepage()
    assert homepage["sections"][0]["title"] == "B"


def test_get_section():
    svc = MarketplaceHomeService()
    svc.add_section("trending", "Trending", "trending", [{"id": "e1"}])
    section = svc.get_section("trending")
    assert section is not None
    assert len(section.items) == 1
