from app.services.app_marketplace_complete_app_page import build_complete_app_page

def test_complete():
    p = build_complete_app_page(
        app={"name": "X", "slug": "x", "category": "connector", "manifest": {"sandbox": {"runtime": "python3.12"}}},
        developer={"name": "Dev"}, versions=[{"version": "2.0"}],
        stats={"installs": 100, "executions": 500, "webhooks": 200},
        health={"score": 95}, badges=[{"label": "Popular"}],
        reviews={"average": 4.5, "count": 20}, related=[{"name": "Y"}],
        permissions=["read:cohorts", "write:cohorts"], network_hosts=["api.example.com"], secrets_count=2,
    )
    assert p["page_type"] == "app_detail"
    assert p["stats_card"] is not None
    assert p["privacy"]["risk_level"] in ("low", "medium", "high")
    assert len(p["sections"]) == 6

def test_minimal():
    p = build_complete_app_page(
        app={"name": "Min"}, developer={}, versions=[], stats={},
        health={}, badges=[], reviews={}, related=[],
        permissions=[], network_hosts=[], secrets_count=0,
    )
    assert p["page_type"] == "app_detail"
