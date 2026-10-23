from app.services.app_marketplace_app_app_kanban_board import build_kanban_board

def test_board():
    cols = [
        {"id": "todo", "title": "To Do", "cards": [
            {"id": "1", "title": "Fix bug", "assignee": "Alice", "priority": "high"},
        ]},
        {"id": "done", "title": "Done", "wip_limit": 5, "cards": []},
    ]
    r = build_kanban_board(columns=cols)
    assert r["total_cards"] == 1
    assert len(r["columns"]) == 2
    assert r["columns"][0]["card_count"] == 1
    assert not r["columns"][1]["over_limit"]

def test_wip_over():
    cols = [{"id": "wip", "title": "In Progress", "wip_limit": 1,
             "cards": [{"id": "1", "title": "A"}, {"id": "2", "title": "B"}]}]
    r = build_kanban_board(columns=cols)
    assert r["columns"][0]["over_limit"]
