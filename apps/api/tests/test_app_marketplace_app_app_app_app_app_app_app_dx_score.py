from app.services.app_marketplace_app_app_app_app_app_app_app_dx_score import compute_dx_score

def test_high_score():
    r = compute_dx_score(docs_coverage=0.95, sdk_languages=5, avg_onboarding_min=5,
                           api_uptime=99.99, support_response_hours=2,
                           sandbox_available=True, cli_available=True,
                           changelog_frequency="weekly")
    assert r["grade"] in ("A+", "A")
    assert r["score"] >= 85

def test_low_score():
    r = compute_dx_score(docs_coverage=0.3, sdk_languages=1, avg_onboarding_min=30,
                           api_uptime=98, support_response_hours=48,
                           sandbox_available=False, cli_available=False,
                           changelog_frequency="quarterly")
    assert r["grade"] in ("C", "D")
    assert r["score"] < 50
