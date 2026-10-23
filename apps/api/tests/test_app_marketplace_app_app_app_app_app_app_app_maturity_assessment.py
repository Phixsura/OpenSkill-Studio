from app.services.app_marketplace_app_app_app_app_app_app_app_maturity_assessment import assess_maturity

def test_maturity():
    scores = {"ci_cd": 5, "observability": 4, "security": 4,
              "reliability": 3, "scalability": 3, "developer_experience": 5}
    r = assess_maturity(scores)
    assert r["overall_level"] == 4
    assert r["overall_name"] == "Measured"
    assert r["dimension_count"] == 6
    assert "CI/CD" in r["strengths"]
    assert "Developer Experience" in r["strengths"]
    assert len(r["improvements"]) == 0
    assert "2,150" in r["milestone"]
