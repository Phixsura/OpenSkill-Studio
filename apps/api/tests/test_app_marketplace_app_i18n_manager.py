from app.services.app_marketplace_app_i18n_manager import get_translation_coverage, find_unused_keys

def test_coverage():
    translations = {
        "en": {"hello": "Hello", "bye": "Goodbye", "save": "Save"},
        "es": {"hello": "Hola", "bye": "Adiós"},
        "fr": {"hello": "Bonjour"},
    }
    r = get_translation_coverage(translations=translations)
    assert r["total_keys"] == 3
    en = next(c for c in r["locales"] if c["locale"] == "en")
    assert en["complete"]
    es = next(c for c in r["locales"] if c["locale"] == "es")
    assert es["coverage_pct"] == 66.7
    assert "save" in es["missing_keys"]

def test_unused():
    r = find_unused_keys(used_keys={"hello", "bye"}, defined_keys={"hello", "bye", "old_key"})
    assert r["unused"] == ["old_key"]
    assert r["missing_count"] == 0
