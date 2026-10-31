from app.services.app_marketplace_app_app_user_avatar_stack import build_avatar_stack

def test_stack():
    users = [{"name": "Alice"}, {"name": "Bob"}, {"name": "Carol"},
             {"name": "Dave"}, {"name": "Eve"}, {"name": "Frank"}, {"name": "Grace"}]
    r = build_avatar_stack(users=users, max_display=5)
    assert len(r["avatars"]) == 5
    assert r["remaining"] == 2
    assert r["remaining_label"] == "+2"
    assert r["avatars"][0]["initials"] == "A"

def test_few():
    r = build_avatar_stack(users=[{"name": "Alice Smith"}], max_display=5)
    assert r["remaining"] == 0
    assert not r["show_remaining"]
    assert r["avatars"][0]["initials"] == "AS"
