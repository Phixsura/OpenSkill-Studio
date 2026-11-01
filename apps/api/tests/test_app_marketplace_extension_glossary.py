from app.services.app_marketplace_extension_glossary import PlatformGlossaryService


def test_add_and_lookup():
    svc = PlatformGlossaryService()
    svc.add_term("Sandbox", "Isolated execution environment", "runtime")
    term = svc.lookup("sandbox")
    assert term is not None
    assert term.definition == "Isolated execution environment"


def test_search():
    svc = PlatformGlossaryService()
    svc.add_term("Webhook", "HTTP callback", "api")
    svc.add_term("Extension", "Add-on module", "platform")
    results = svc.search("callback")
    assert len(results) == 1


def test_categories():
    svc = PlatformGlossaryService()
    svc.add_term("A", "d", "api")
    svc.add_term("B", "d", "runtime")
    svc.add_term("C", "d", "api")
    assert svc.get_categories() == ["api", "runtime"]
    assert len(svc.get_by_category("api")) == 2


def test_related():
    svc = PlatformGlossaryService()
    svc.add_term("Webhook", "HTTP callback", "api", related=["Extension"])
    svc.add_term("Extension", "Add-on", "platform")
    related = svc.get_related("webhook")
    assert len(related) == 1
    assert related[0].term == "Extension"
