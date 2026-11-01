from app.services.app_developer_invite import create_invite, accept_invite, list_pending_invites, revoke_invite

def test_create():
    i = create_invite(developer_id="d1", email="new@x.com", role="admin")
    assert i["status"] == "pending"
    assert len(i["code"]) > 20

def test_accept():
    i = create_invite(developer_id="d2", email="a@b.c")
    result = accept_invite(i["code"], user_id="u1")
    assert result is not None
    assert result["status"] == "accepted"

def test_accept_twice():
    i = create_invite(developer_id="d3", email="x@y.z")
    accept_invite(i["code"], user_id="u1")
    assert accept_invite(i["code"], user_id="u2") is None

def test_list_pending():
    create_invite(developer_id="d4", email="p@q.r")
    pending = list_pending_invites("d4")
    assert len(pending) >= 1

def test_revoke():
    i = create_invite(developer_id="d5", email="r@s.t")
    assert revoke_invite(i["code"]) is True
    assert accept_invite(i["code"], user_id="u1") is None

def test_revoke_nonexistent():
    assert revoke_invite("fake") is False
