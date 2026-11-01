from app.services.app_marketplace_extension_feature_announcer import FeatureAnnouncerService

def test_announce_and_get():
    svc = FeatureAnnouncerService()
    svc.announce("f1", "Dark Mode", "New dark theme", "ui", "🌙")
    new = svc.get_new("user-1")
    assert len(new) == 1

def test_dismiss():
    svc = FeatureAnnouncerService()
    svc.announce("f1", "Feature", "Desc", "ui")
    svc.dismiss("user-1", "f1")
    assert len(svc.get_new("user-1")) == 0
    assert len(svc.get_new("user-2")) == 1
