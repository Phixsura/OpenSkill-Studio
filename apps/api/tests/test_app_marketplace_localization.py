from app.services.app_marketplace_localization import add_translation, get_localized_listing, get_translation_coverage

def test_add():
    r = add_translation(app_id="a1", locale="zh", fields={"name": "我的应用", "description": "描述"})
    assert r["locale"] == "zh"

def test_invalid_locale():
    r = add_translation(app_id="a1", locale="xx", fields={"name": "X"})
    assert r["error"]

def test_invalid_field():
    r = add_translation(app_id="a1", locale="zh", fields={"price": "free"})
    assert r["error"]

def test_localized():
    app = {"name": "My App", "description": "Desc"}
    translations = {"zh": {"name": "我的应用"}}
    l = get_localized_listing(app=app, translations=translations, locale="zh")
    assert l["name"] == "我的应用"
    assert l["is_translated"]

def test_fallback():
    l = get_localized_listing(app={"name": "My App"}, translations={}, locale="ja")
    assert l["name"] == "My App"
    assert not l["is_translated"]

def test_coverage():
    c = get_translation_coverage(translations={"zh": {"name": "X"}, "ja": {"name": "Y"}})
    assert c["translated_count"] == 2
