from app.services.app_marketplace_app_localization import get_localization_status, validate_translation

def test_status():
    translations = {"en": {"title": "My App", "description": "Desc", "screenshots": True, "changelog": "v1"},
                    "es": {"title": "Mi App"}}
    r = get_localization_status(app_id="a1", translations=translations)
    assert r["supported_count"] == 8
    en = next(l for l in r["locales"] if l["locale"] == "en")
    assert en["progress"] == 100
    es = next(l for l in r["locales"] if l["locale"] == "es")
    assert es["progress"] == 25

def test_validate_ok():
    r = validate_translation(locale="fr", title="Mon App", description="Une application formidable pour les devs")
    assert r["valid"]

def test_validate_fail():
    r = validate_translation(locale="en", title="Hi", description="Short")
    assert not r["valid"]
    assert len(r["errors"]) == 2
