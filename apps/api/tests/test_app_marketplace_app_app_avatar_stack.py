from app.services.app_marketplace_app_app_avatar_stack import build_avatar_stack

def test_basic():
    users = [{"name": "Alice", "email": "a@b.com"}, {"name": "Bob", "email": "b@b.com"}]
    r = build_avatar_stack(users=users)
    assert r["total"] == 2
    assert r["overflow_count"] == 0
    assert r["avatars"][0]["initials"] == "A"
    assert "gravatar.com" in r["avatars"][0]["avatar_url"]

def test_overflow():
    users = [{"name": f"User {i}"} for i in range(8)]
    r = build_avatar_stack(users=users, max_display=3)
    assert len(r["avatars"]) == 3
    assert r["overflow_count"] == 5
    assert r["overflow_text"] == "+5"

def test_xss():
    r = build_avatar_stack(users=[{"name": "<img onerror=alert(1)>"}])
    assert "<img" not in r["avatars"][0]["name"]
