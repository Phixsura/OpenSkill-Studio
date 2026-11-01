from app.services.app_marketplace_app_api_key_rotation_policy import rotate_api_key, get_rotation_policy

def test_rotate():
    r = rotate_api_key(current_key_prefix="sk_old1", overlap_hours=48)
    assert len(r["new_key"]) > 20
    assert r["new_key_prefix"] == r["new_key"][:8]
    assert "48h" in r["message"]

def test_policy_auto():
    r = get_rotation_policy(max_age_days=60, auto_rotate=True)
    assert r["auto_rotate"]
    assert "60 days" in r["policy_summary"]

def test_policy_manual():
    r = get_rotation_policy(auto_rotate=False)
    assert "Manual" in r["policy_summary"]
