from app.services.app_marketplace_app_app_app_app_app_app_app_resource_tagger import ResourceTagger

def test_tagger():
    t = ResourceTagger()
    t.tag("i-001", tags={"env": "prod", "team": "platform"})
    t.tag("i-002", tags={"env": "prod", "team": "data"})
    t.tag("i-003", tags={"env": "staging", "team": "platform"})
    assert t.query(tag_key="env", tag_value="prod") == ["i-001", "i-002"]
    assert t.query(tag_key="team", tag_value="platform") == ["i-001", "i-003"]
    c = t.cost_by_tag("team", {"i-001": 100, "i-002": 200, "i-003": 50})
    assert c["breakdown"]["platform"] == 150
    assert c["breakdown"]["data"] == 200
    s = t.stats()
    assert s["total_resources"] == 3
    assert s["unique_tag_keys"] == 2
