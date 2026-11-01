from app.services.app_marketplace_extension_listing_builder import ExtListingBuilderService

def test_create_and_update():
    svc = ExtListingBuilderService()
    svc.create("ext-1")
    svc.update("ext-1", name="My Extension", tagline="Best extension")
    listing = svc.get("ext-1")
    assert listing.name == "My Extension"

def test_completeness():
    svc = ExtListingBuilderService()
    svc.create("ext-1")
    assert svc.get("ext-1").completeness() == 12  # only pricing=free
    svc.update("ext-1", name="X", tagline="Y", description="Z"*20, category="tools")
    assert svc.get("ext-1").completeness() >= 62

def test_publish_fails():
    svc = ExtListingBuilderService()
    svc.create("ext-1")
    ok, errors = svc.publish("ext-1")
    assert ok is False
    assert "Name is required" in errors

def test_publish_success():
    svc = ExtListingBuilderService()
    svc.create("ext-1")
    svc.update("ext-1", name="App", tagline="Tag", description="A"*25, category="tools")
    ok, errors = svc.publish("ext-1")
    assert ok is True
    assert svc.get("ext-1").draft is False
