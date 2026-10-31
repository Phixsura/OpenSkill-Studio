from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_lint_score import fleet_lint_score
def test_lint():
    r = fleet_lint_score([{"lint_errors": 0}, {"lint_errors": 0}, {"lint_errors": 5}])
    assert r["clean"] == 2
    assert r["clean_pct"] == 66.7
    assert not r["excellent"]
