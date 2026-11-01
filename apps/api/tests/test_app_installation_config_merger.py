from app.services.app_installation_config_merger import merge_installation_config, diff_config

def test_defaults_only():
    r = merge_installation_config(app_defaults={"url": "https://x.com", "timeout": 30})
    assert r["url"] == "https://x.com"

def test_override():
    r = merge_installation_config(app_defaults={"url": "https://x.com", "timeout": 30}, org_overrides={"timeout": 60})
    assert r["timeout"] == 60
    assert r["url"] == "https://x.com"

def test_no_mutation():
    defaults = {"a": 1}
    merge_installation_config(app_defaults=defaults, org_overrides={"a": 2})
    assert defaults["a"] == 1

def test_diff_no_changes():
    d = diff_config({"a": 1}, {"a": 1})
    assert d["has_changes"] is False

def test_diff_added():
    d = diff_config({}, {"a": 1})
    assert "a" in d["added"]

def test_diff_removed():
    d = diff_config({"a": 1}, {})
    assert "a" in d["removed"]

def test_diff_changed():
    d = diff_config({"a": 1}, {"a": 2})
    assert d["changed"]["a"]["from"] == 1
    assert d["changed"]["a"]["to"] == 2
