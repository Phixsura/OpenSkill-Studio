from app.services.app_marketplace_app_developer_app_config_templates import list_templates, apply_template, diff_with_template

def test_list():
    t = list_templates()
    assert len(t) == 4
    assert any(x["id"] == "production" for x in t)

def test_apply():
    r = apply_template(template_id="production")
    assert r["config"]["retries"] == 5

def test_apply_override():
    r = apply_template(template_id="minimal", overrides={"timeout_ms": 999})
    assert r["config"]["timeout_ms"] == 999

def test_unknown():
    r = apply_template(template_id="nope")
    assert r["error"]

def test_diff():
    d = diff_with_template(current_config={"timeout_ms": 5000, "retries": 3, "logging": "warn", "cache_ttl": 300},
                            template_id="balanced")
    assert d["matches_template"]

def test_diff_changed():
    d = diff_with_template(current_config={"timeout_ms": 9999}, template_id="balanced")
    assert not d["matches_template"]
    assert d["diff_count"] > 0
