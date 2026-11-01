from app.services.app_marketplace_complete_team_page import build_complete_team_page

def test_page():
    team = [{"role": "owner", "status": "active"}, {"role": "developer", "status": "active"}]
    p = build_complete_team_page(team=team, pending_invites=[{"email": "x@y.com"}],
                                   activity=[{"type": "member_added"}], plan_limit=5)
    assert p["stats"]["total"] == 2
    assert p["stats"]["seats_remaining"] == 3
    assert p["can_invite"]

def test_full():
    team = [{"role": "owner", "status": "active"}] * 3
    p = build_complete_team_page(team=team, pending_invites=[], activity=[], plan_limit=3)
    assert not p["can_invite"]
    assert p["stats"]["seats_remaining"] == 0
