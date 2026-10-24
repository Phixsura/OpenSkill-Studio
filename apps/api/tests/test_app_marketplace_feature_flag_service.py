from app.services.app_marketplace_feature_flag_service import evaluate_flags, create_flag

def test_evaluate():
    r = evaluate_flags(user_id="u1", org_id="org1")
    assert r["total"] == 5
    assert isinstance(r["flags"]["dark_mode"], bool)
    assert r["flags"]["beta_analytics"] is False  # rollout=0

def test_create():
    r = create_flag(name="my_flag", description="Test", rollout=50)
    assert r["created"]
    assert r["rollout"] == 50

def test_invalid_name():
    r = create_flag(name="bad flag!", description="X")
    assert "error" in r
