from app.services.app_marketplace_app_app_app_app_app_app_app_avatar_gen import generate_avatar, generate_group_avatars

def test_avatar():
    a = generate_avatar(name="Alice Chen", size=40)
    assert a["initials"] == "AC"
    assert a["bg_color"].startswith("#")
    assert "<svg" in a["svg"]
    assert "AC" in a["svg"]

def test_group():
    names = ["Alice", "Bob", "Carol", "Dave", "Eve", "Frank", "Grace"]
    g = generate_group_avatars(names, max_show=5)
    assert len(g["avatars"]) == 5
    assert g["remaining"] == 2
    assert g["remaining_display"] == "+2"
    assert g["total"] == 7
