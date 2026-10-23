from app.services.app_marketplace_app_app_localization import build_locale_bundle, get_string

BASE = {"greeting": "Hello", "farewell": "Goodbye", "save": "Save"}
TRANSLATIONS = {
    "es": {"greeting": "Hola", "farewell": "Adiós", "save": "Guardar"},
    "fr": {"greeting": "Bonjour", "farewell": "Au revoir"},
}

def test_bundle():
    r = build_locale_bundle(base=BASE, translations=TRANSLATIONS)
    assert r["locale_count"] == 2
    assert r["locales"]["es"]["complete"]
    assert r["locales"]["es"]["coverage_pct"] == 100.0
    assert not r["locales"]["fr"]["complete"]
    assert "save" in r["locales"]["fr"]["missing"]

def test_get_string():
    bundle = build_locale_bundle(base=BASE, translations=TRANSLATIONS)
    assert get_string(key="greeting", locale="es", bundle=bundle) == "Hola"
    assert get_string(key="save", locale="fr", bundle=bundle) == "save"  # fallback to key
