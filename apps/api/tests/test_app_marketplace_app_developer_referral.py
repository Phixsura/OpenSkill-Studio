from app.services.app_marketplace_app_developer_referral import generate_referral_code, create_referral, process_referral_signup, get_referral_stats

def test_code():
    c = generate_referral_code(developer_id="d1")
    assert c.startswith("ref_")
    assert len(c) == 12

def test_create():
    r = create_referral(referrer_id="d1", code="ref_abc")
    assert r["signups"] == 0

def test_signup():
    r = create_referral(referrer_id="d1", code="ref_abc")
    r = process_referral_signup(referral=r)
    assert r["signups"] == 1
    assert r["total_reward_cents"] == 500

def test_stats():
    refs = [{"signups": 5, "total_reward_cents": 2500}, {"signups": 3, "total_reward_cents": 1500}]
    s = get_referral_stats(referrals=refs)
    assert s["total_signups"] == 8
    assert "$40.00" in s["total_rewards"]
