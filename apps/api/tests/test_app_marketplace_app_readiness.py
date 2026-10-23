from app.services.app_marketplace_app_readiness import readiness_check
def test_ready():
    assert readiness_check()["ready"]
def test_not_ready():
    assert not readiness_check(db_ok=False)["ready"]
