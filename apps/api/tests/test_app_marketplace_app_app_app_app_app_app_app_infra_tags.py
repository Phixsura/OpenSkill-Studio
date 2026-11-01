from app.services.app_marketplace_app_app_app_app_app_app_app_infra_tags import (
    validate_tags, tag_compliance_report, suggest_tags,
)

def test_validate():
    r = validate_tags("api-server", {"env": "prod", "team": "platform", "cost_center": "eng", "service": "api"})
    assert r["compliant"]
    r2 = validate_tags("db", {"env": "prod"})
    assert not r2["compliant"]
    assert len(r2["missing"]) == 3

def test_report():
    resources = [
        {"name": "api", "tags": {"env": "p", "team": "t", "cost_center": "c", "service": "s"}},
        {"name": "db", "tags": {"env": "p"}},
    ]
    r = tag_compliance_report(resources)
    assert r["compliant"] == 1
    assert r["compliance_pct"] == 50

def test_suggest():
    r = suggest_tags("prod-db", "database")
    assert "backup" in r["suggested_tags"]
