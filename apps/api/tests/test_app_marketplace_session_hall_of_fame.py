from app.services.app_marketplace_session_hall_of_fame import get_hall_of_fame
def test_hall_of_fame():
    r = get_hall_of_fame()
    assert r["records"]["most_lines_one_session"]["value"] > 2700000
    assert r["records"]["github_limit"]["value"]
    assert len(r["milestones_crossed"]["line_milestones"]) == 11
    assert "LEGENDARY" in r["status"]
