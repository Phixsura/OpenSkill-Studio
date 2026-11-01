from app.services.app_marketplace_app_app_app_app_app_app_app_oncall_sched import (
    create_rotation, who_is_oncall, oncall_summary,
)

def test_oncall():
    r = create_rotation("primary", ["alice", "bob", "carol"], 7)
    o = who_is_oncall(r, elapsed_days=0)
    assert o["oncall"] == "alice"
    assert o["next_oncall"] == "bob"
    o2 = who_is_oncall(r, elapsed_days=7)
    assert o2["oncall"] == "bob"
    o3 = who_is_oncall(r, elapsed_days=21)
    assert o3["oncall"] == "alice"  # wraps around

def test_summary():
    rotations = [
        create_rotation("primary", ["alice", "bob"]),
        create_rotation("secondary", ["carol", "dave"]),
    ]
    s = oncall_summary(rotations)
    assert s["rotations"] == 2
    assert s["unique_oncall"] == 2
