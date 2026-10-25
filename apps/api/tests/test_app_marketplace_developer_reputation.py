from app.services.app_marketplace_developer_reputation import (
    DeveloperReputationService, ReputationFactors, ReputationTier,
)


def test_new_developer():
    rs = DeveloperReputationService()
    score = rs.calculate_score(ReputationFactors())
    assert score == 0
    assert rs.get_tier(score) == ReputationTier.NEW


def test_good_developer():
    rs = DeveloperReputationService()
    factors = ReputationFactors(
        extension_count=5, avg_rating=4.5, total_downloads=10000,
        security_incidents=0, support_response_hours=2.0,
        review_response_rate=0.9, policy_violations=0,
        community_contributions=10, account_age_days=365,
    )
    score = rs.calculate_score(factors)
    assert score >= 400  # at least bronze
    assert rs.get_tier(score) in (ReputationTier.BRONZE, ReputationTier.SILVER, ReputationTier.GOLD, ReputationTier.PLATINUM)


def test_security_penalty():
    rs = DeveloperReputationService()
    clean = ReputationFactors(extension_count=5, avg_rating=4.0, total_downloads=1000)
    dirty = ReputationFactors(extension_count=5, avg_rating=4.0, total_downloads=1000, security_incidents=2)
    assert rs.calculate_score(clean) > rs.calculate_score(dirty)


def test_policy_violation_penalty():
    rs = DeveloperReputationService()
    clean = ReputationFactors(extension_count=3, avg_rating=4.0)
    violator = ReputationFactors(extension_count=3, avg_rating=4.0, policy_violations=1)
    assert rs.calculate_score(clean) > rs.calculate_score(violator)


def test_update_and_get():
    rs = DeveloperReputationService()
    result = rs.update("dev-1", ReputationFactors(extension_count=8, avg_rating=4.8,
                        total_downloads=50000, account_age_days=500))
    assert result["score"] > 0
    rep = rs.get_reputation("dev-1")
    assert rep is not None
    assert rep["score"] == result["score"]


def test_leaderboard():
    rs = DeveloperReputationService()
    rs.update("dev-a", ReputationFactors(avg_rating=5.0, total_downloads=100000, extension_count=10))
    rs.update("dev-b", ReputationFactors(avg_rating=3.0, extension_count=1))
    rs.update("dev-c", ReputationFactors(avg_rating=4.0, total_downloads=5000, extension_count=5))
    board = rs.get_leaderboard(3)
    assert board[0]["developer_id"] == "dev-a"
    assert board[0]["score"] >= board[1]["score"]


def test_tier_thresholds():
    rs = DeveloperReputationService()
    assert rs.get_tier(0) == ReputationTier.NEW
    assert rs.get_tier(200) == ReputationTier.BRONZE
    assert rs.get_tier(500) == ReputationTier.SILVER
    assert rs.get_tier(800) == ReputationTier.GOLD
    assert rs.get_tier(1200) == ReputationTier.PLATINUM
