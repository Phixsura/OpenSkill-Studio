from app.services.app_marketplace_extension_i18n import ExtensionI18n, TranslationBundle


def test_basic_translation():
    i18n = ExtensionI18n()
    i18n.register_bundle("ext-1", TranslationBundle("en", {"greeting": "Hello", "bye": "Goodbye"}))
    i18n.register_bundle("ext-1", TranslationBundle("zh-CN", {"greeting": "你好"}))
    assert i18n.get_message("ext-1", "greeting", "en") == "Hello"
    assert i18n.get_message("ext-1", "greeting", "zh-CN") == "你好"


def test_fallback_chain():
    i18n = ExtensionI18n()
    i18n.register_bundle("ext-2", TranslationBundle("en", {"title": "Dashboard"}))
    # zh-TW falls back to zh-CN then to en
    assert i18n.get_message("ext-2", "title", "zh-TW") == "Dashboard"


def test_missing_key_returns_key():
    i18n = ExtensionI18n()
    i18n.register_bundle("ext-3", TranslationBundle("en", {}))
    assert i18n.get_message("ext-3", "unknown.key") == "unknown.key"


def test_parameter_interpolation():
    i18n = ExtensionI18n()
    i18n.register_bundle("ext-4", TranslationBundle("en", {
        "welcome": "Welcome, {name}! You have {count} extensions.",
    }))
    msg = i18n.get_message("ext-4", "welcome", params={"name": "Alice", "count": "5"})
    assert msg == "Welcome, Alice! You have 5 extensions."


def test_supported_locales():
    i18n = ExtensionI18n()
    i18n.register_bundle("ext-5", TranslationBundle("en", {"a": "1"}))
    i18n.register_bundle("ext-5", TranslationBundle("ja", {"a": "1"}))
    i18n.register_bundle("ext-5", TranslationBundle("fr", {"a": "1"}))
    assert i18n.get_supported_locales("ext-5") == ["en", "fr", "ja"]


def test_translation_coverage():
    i18n = ExtensionI18n()
    i18n.register_bundle("ext-6", TranslationBundle("en", {"a": "1", "b": "2", "c": "3", "d": "4"}))
    i18n.register_bundle("ext-6", TranslationBundle("ja", {"a": "あ", "b": "い"}))
    cov = i18n.get_translation_coverage("ext-6", "ja")
    assert cov["total"] == 4
    assert cov["translated"] == 2
    assert cov["missing"] == 2
    assert cov["coverage"] == 50.0


def test_export_bundle():
    i18n = ExtensionI18n()
    i18n.register_bundle("ext-7", TranslationBundle("ko", {"hello": "안녕하세요"}))
    exported = i18n.export_bundle("ext-7", "ko")
    assert exported == {"hello": "안녕하세요"}
