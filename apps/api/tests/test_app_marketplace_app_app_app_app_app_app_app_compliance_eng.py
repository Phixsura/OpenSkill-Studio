from app.services.app_marketplace_app_app_app_app_app_app_app_compliance_eng import evaluate_policy, compliance_score

def test_compliant():
    r = evaluate_policy(
        {"name": "prod-db", "encryption": "aes256", "region": "us-east"},
        [{"name": "encryption_required", "field": "encryption", "rule": "required"},
         {"name": "valid_region", "field": "region", "rule": "one_of", "values": ["us-east", "eu-west"]}])
    assert r["compliant"]

def test_violations():
    r = evaluate_policy(
        {"name": "test-db"},
        [{"name": "enc", "field": "encryption", "rule": "required", "severity": "critical"}])
    assert not r["compliant"]
    assert r["critical_violations"] == 1

def test_score():
    r = compliance_score([{"compliant": True}, {"compliant": True}, {"compliant": False}])
    assert r["score"] == 66.7
