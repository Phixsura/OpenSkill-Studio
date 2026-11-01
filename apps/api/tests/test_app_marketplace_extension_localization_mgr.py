from app.services.app_marketplace_extension_localization_mgr import ExtLocalizationMgrService

def test_set_and_get():
    svc = ExtLocalizationMgrService()
    svc.set("ext-1", "en", name="Auth Plugin", tagline="Authentication", description="Full auth")
    svc.set("ext-1", "zh", name="认证插件", tagline="认证", description="完整认证")
    lc = svc.get("ext-1", "zh")
    assert lc.name == "认证插件"

def test_fallback():
    svc = ExtLocalizationMgrService()
    svc.set("ext-1", "en", name="Auth Plugin")
    lc = svc.get("ext-1", "fr")  # falls back to en
    assert lc.name == "Auth Plugin"

def test_locales():
    svc = ExtLocalizationMgrService()
    svc.set("ext-1", "en", name="A")
    svc.set("ext-1", "ja", name="あ")
    assert set(svc.get_locales("ext-1")) == {"en", "ja"}

def test_completeness():
    svc = ExtLocalizationMgrService()
    svc.set("ext-1", "en", name="A", tagline="B", description="C")
    svc.set("ext-1", "zh", name="甲")
    comp = svc.get_completeness("ext-1")
    assert comp["en"] == 100
    assert comp["zh"] == 33
