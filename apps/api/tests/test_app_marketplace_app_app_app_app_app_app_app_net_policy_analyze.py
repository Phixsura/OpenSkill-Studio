from app.services.app_marketplace_app_app_app_app_app_app_app_net_policy_analyze import analyze_policies

def test_analyze():
    r = analyze_policies([
        {"name": "allow-http", "action": "allow", "namespace": "prod", "source": "web", "destination": "api"},
        {"name": "deny-external", "action": "deny", "namespace": "prod", "source": "*", "destination": "db"},
        {"name": "bad-rule", "action": "allow", "namespace": "dev", "source": "*", "destination": "*"},
    ])
    assert r["total"] == 3
    assert r["allow"] == 2
    assert len(r["overly_permissive"]) == 1
    assert r["security_score"] == 80
