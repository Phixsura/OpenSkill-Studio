from app.services.app_marketplace_extension_developer_score import DeveloperScoreService


def test_set_and_calculate():
    dss = DeveloperScoreService()
    dss.set_all_dimensions("dev-1", {
        "code_quality": 90, "community": 80, "responsiveness": 85,
        "reliability": 95, "adoption": 70,
    })
    score = dss.calculate_score("dev-1")
    assert 80 <= score <= 95


def test_grade():
    dss = DeveloperScoreService()
    assert dss.get_grade(95) == "A+"
    assert dss.get_grade(85) == "A"
    assert dss.get_grade(75) == "B"
    assert dss.get_grade(55) == "D"
    assert dss.get_grade(30) == "F"


def test_breakdown():
    dss = DeveloperScoreService()
    dss.set_dimension("dev-2", "code_quality", 90)
    dss.set_dimension("dev-2", "reliability", 60)
    breakdown = dss.get_breakdown("dev-2")
    assert len(breakdown) == 5
    cq = next(d for d in breakdown if d.name == "code_quality")
    assert cq.value == 90


def test_improvement_tips():
    dss = DeveloperScoreService()
    dss.set_all_dimensions("dev-3", {
        "code_quality": 90, "community": 40, "responsiveness": 50,
        "reliability": 95, "adoption": 30,
    })
    tips = dss.get_improvement_tips("dev-3")
    assert len(tips) >= 3
    assert tips[0]["impact"] >= tips[-1]["impact"]


def test_leaderboard():
    dss = DeveloperScoreService()
    dss.set_all_dimensions("top", {"code_quality": 95, "community": 90, "responsiveness": 95, "reliability": 98, "adoption": 85})
    dss.set_all_dimensions("mid", {"code_quality": 60, "community": 50, "responsiveness": 55, "reliability": 65, "adoption": 40})
    board = dss.get_leaderboard()
    assert board[0]["developer_id"] == "top"
    assert board[0]["score"] > board[1]["score"]


def test_empty_score():
    dss = DeveloperScoreService()
    assert dss.calculate_score("unknown") == 0.0
