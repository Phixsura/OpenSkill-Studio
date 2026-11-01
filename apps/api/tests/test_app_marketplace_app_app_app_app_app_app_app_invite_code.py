from app.services.app_marketplace_app_app_app_app_app_app_app_invite_code import (
    create_code, redeem_code, code_stats, clear_codes,
)

def test_create_redeem():
    clear_codes()
    c = create_code("admin", max_uses=2)
    r = redeem_code(c["code"], "user1")
    assert r["redeemed"]
    assert r["remaining"] == 1
    r2 = redeem_code(c["code"], "user1")
    assert not r2["redeemed"]  # already redeemed
    r3 = redeem_code(c["code"], "user2")
    assert r3["redeemed"]
    r4 = redeem_code(c["code"], "user3")
    assert not r4["redeemed"]  # max uses
    clear_codes()

def test_stats():
    clear_codes()
    create_code("a", max_uses=5)
    c2 = create_code("b", max_uses=1)
    redeem_code(c2["code"], "x")
    s = code_stats()
    assert s["total_codes"] == 2
    assert s["active"] == 1
    assert s["total_redemptions"] == 1
    clear_codes()
