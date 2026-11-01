from app.services.app_marketplace_invite_system import InviteSystem


def test_create_and_redeem_code():
    inv = InviteSystem()
    code = inv.create_invite_code("ext-1", "dev-1", max_uses=5)
    assert len(code.code) == 8
    ok, msg = inv.redeem_code(code.code, "user-1")
    assert ok is True
    assert "Access granted" in msg


def test_max_uses_enforced():
    inv = InviteSystem()
    code = inv.create_invite_code("ext-2", "dev-2", max_uses=1)
    inv.redeem_code(code.code, "user-1")
    ok, msg = inv.redeem_code(code.code, "user-2")
    assert ok is False
    assert "maximum uses" in msg


def test_duplicate_redeem_blocked():
    inv = InviteSystem()
    code = inv.create_invite_code("ext-3", "dev-3", max_uses=10)
    inv.redeem_code(code.code, "user-1")
    ok, msg = inv.redeem_code(code.code, "user-1")
    assert ok is False
    assert "already redeemed" in msg


def test_deactivate_code():
    inv = InviteSystem()
    code = inv.create_invite_code("ext-4", "dev-4")
    inv.deactivate_code(code.code)
    ok, _ = inv.redeem_code(code.code, "user-1")
    assert ok is False


def test_beta_enrollment():
    inv = InviteSystem()
    inv.create_beta("ext-5", "Beta v2", capacity=2)
    ok1, _ = inv.enroll_beta("ext-5", "u1")
    ok2, _ = inv.enroll_beta("ext-5", "u2")
    assert ok1 and ok2
    ok3, msg = inv.enroll_beta("ext-5", "u3")
    assert ok3 is False
    assert "waitlist" in msg


def test_beta_status():
    inv = InviteSystem()
    inv.create_beta("ext-6", "Early Access", capacity=10)
    inv.enroll_beta("ext-6", "u1")
    status = inv.get_beta_status("ext-6")
    assert status["enrolled"] == 1
    assert status["available_slots"] == 9
