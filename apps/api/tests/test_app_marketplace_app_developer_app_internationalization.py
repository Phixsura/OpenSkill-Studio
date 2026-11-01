from app.services.app_marketplace_app_developer_app_internationalization import (
    create_locale_bundle, get_translated_string, compute_translation_completeness, merge_locale_bundles,
)

def test_create():
    b = create_locale_bundle(app_id="a1", locale="zh", strings={"greeting": "你好", "bye": "再见"})
    assert b["string_count"] == 2

def test_invalid_locale():
    b = create_locale_bundle(app_id="a1", locale="", strings={})
    assert b["error"]

def test_get_translated():
    bundles = {"en": {"greeting": "Hello"}, "zh": {"greeting": "你好"}}
    assert get_translated_string(key="greeting", locale="zh", bundles=bundles) == "你好"

def test_fallback():
    bundles = {"en": {"greeting": "Hello"}, "zh": {}}
    assert get_translated_string(key="greeting", locale="zh", bundles=bundles) == "Hello"

def test_completeness():
    r = compute_translation_completeness(base_keys=["a", "b", "c"], translated_keys=["a", "b"])
    assert r["completeness_pct"] > 60
    assert r["missing"] == ["c"]
    assert not r["complete"]

def test_merge():
    r = merge_locale_bundles(base={"a": "1", "b": "2"}, override={"b": "override", "c": "3"})
    assert r["b"] == "override"
    assert r["c"] == "3"
