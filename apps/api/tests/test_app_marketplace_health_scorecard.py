from app.services.app_marketplace_health_scorecard import compute_health_scorecard, get_improvement_recommendations

def test_excellent():
    r = compute_health_scorecard(availability=99.99, performance={"p99_ms": 80},
                                  security={"score": 95}, compliance={"score": 90}, developer_experience={"score": 85})
    assert r["grade"] in ("A+", "A")
    assert r["composite_score"] > 90

def test_poor():
    r = compute_health_scorecard(availability=90, performance={"p99_ms": 2000},
                                  security={"score": 30}, compliance={"score": 20}, developer_experience={"score": 10})
    assert r["grade"] in ("D", "F")

def test_weakest():
    r = compute_health_scorecard(availability=99.9, performance={"p99_ms": 100},
                                  security={"score": 90}, compliance={"score": 40}, developer_experience={"score": 85})
    assert r["weakest_dimension"] == "compliance"

def test_recommendations():
    scorecard = {"dimensions": {"availability": 99, "performance": 60, "security": 70, "compliance": 50, "dx": 40}}
    recs = get_improvement_recommendations(scorecard=scorecard)
    assert len(recs) >= 3
