from app.services.app_marketplace_app_app_app_app_app_app_app_traffic_shaper import TrafficShaper

def test_header_match():
    s = TrafficShaper()
    s.add_rule(name="canary", target="v2", weight=0, match_header="X-Canary", match_value="true")
    s.add_rule(name="stable", target="v1", weight=100)
    r = s.route(headers={"X-Canary": "true"})
    assert r["target"] == "v2"
    assert r["reason"] == "header_match"

def test_weighted():
    s = TrafficShaper()
    s.add_rule(name="v1", target="v1", weight=90)
    s.add_rule(name="v2", target="v2", weight=10)
    d = s.distribution()
    assert d["rules"][0]["pct"] == 90.0
    assert d["rules"][1]["pct"] == 10.0
    r = s.route(user_id="test_user")
    assert r["target"] in ("v1", "v2")
    assert r["reason"] == "weighted"
