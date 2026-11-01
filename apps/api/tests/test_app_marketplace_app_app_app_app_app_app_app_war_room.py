from app.services.app_marketplace_app_app_app_app_app_app_app_war_room import create_war_room, add_update, close_war_room

def test_war_room():
    room = create_war_room("INC-42", "Database Outage", "critical", "alice")
    assert room["status"] == "active"
    r = add_update(room, "bob", "Investigating connection pool")
    assert r["participants"] == 2
    add_update(room, "alice", "Root cause identified")
    c = close_war_room(room, "Connection pool limit increased")
    assert c["closed"]
    assert c["updates"] == 2
