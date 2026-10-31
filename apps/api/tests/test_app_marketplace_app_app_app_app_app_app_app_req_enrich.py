from app.services.app_marketplace_app_app_app_app_app_app_app_req_enrich import enrich_request, build_enrichment_context

def test_enrich():
    r = enrich_request(
        {"method": "GET", "path": "/api/users"},
        [{"field": "request_id", "value": "req-123", "source": "generator"},
         {"field": "tenant_id", "value": "t-1", "source": "auth"},
         {"field": "method", "value": "POST", "source": "override"}])  # won't override existing
    assert r["enrichments_applied"] == 2
    assert r["request"]["request_id"] == "req-123"
    assert r["request"]["method"] == "GET"  # not overridden

def test_context():
    r = build_enrichment_context("u1", "t1", ["dark_mode", "beta"])
    assert r["context_built"]
    assert r["feature_count"] == 2
