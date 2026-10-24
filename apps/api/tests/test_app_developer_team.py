from app.services.app_developer_team import add_member, remove_member, list_members, get_role, has_permission

def test_add():
    m = add_member("t1", user_id="u1", role="admin")
    assert m is not None and m["role"] == "admin"

def test_add_duplicate():
    add_member("t2", user_id="u1")
    assert add_member("t2", user_id="u1") is None

def test_invalid_role():
    assert add_member("t3", user_id="u1", role="superadmin") is None

def test_remove():
    add_member("t4", user_id="u1")
    assert remove_member("t4", "u1") is True

def test_list():
    add_member("t5", user_id="u1", role="owner")
    add_member("t5", user_id="u2", role="member")
    assert len(list_members("t5")) >= 2

def test_role():
    add_member("t6", user_id="u1", role="admin")
    assert get_role("t6", "u1") == "admin"

def test_permission():
    add_member("t7", user_id="u1", role="admin")
    assert has_permission("t7", "u1", min_role="member") is True
    assert has_permission("t7", "u1", min_role="owner") is False

def test_no_permission():
    assert has_permission("t8", "nobody") is False
