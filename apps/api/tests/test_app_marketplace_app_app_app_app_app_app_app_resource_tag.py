from app.services.app_marketplace_app_app_app_app_app_app_app_resource_tag import ResourceTagger

def test_tag_query():
    rt = ResourceTagger()
    rt.tag("vm-1", {"team": "platform", "env": "prod"})
    rt.tag("vm-2", {"team": "data", "env": "prod"})
    rt.tag("vm-3", {"team": "platform", "env": "staging"})
    r = rt.query("team", "platform")
    assert len(r) == 2
    r2 = rt.query("env", "prod")
    assert len(r2) == 2

def test_untag():
    rt = ResourceTagger()
    rt.tag("vm-1", {"team": "x", "temp": "y"})
    rt.untag("vm-1", ["temp"])
    assert "temp" not in rt._resources["vm-1"]["tags"]

def test_untagged():
    rt = ResourceTagger()
    rt.tag("vm-1", {"team": "x"})
    rt.tag("vm-2", {})
    r = rt.untagged(["team"])
    assert "vm-2" in r

def test_summary():
    rt = ResourceTagger()
    rt.tag("a", {"env": "prod"})
    rt.tag("b", {"env": "staging", "team": "x"})
    s = rt.tag_summary()
    assert s["tag_keys"]["env"] == 2
    assert s["tag_keys"]["team"] == 1
