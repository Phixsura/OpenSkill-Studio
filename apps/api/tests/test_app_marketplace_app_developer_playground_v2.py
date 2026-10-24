from app.services.app_marketplace_app_developer_playground_v2 import create_playground_v2, fork_playground, export_playground

def test_create():
    p = create_playground_v2(developer_id="d1", app_id="a1", preset="full")
    assert p["config"]["max_memory_mb"] == 512
    assert len(p["share_id"]) == 10

def test_default():
    p = create_playground_v2(developer_id="d1", app_id="a1")
    assert p["preset"] == "default"

def test_fork():
    f = fork_playground(source_share_id="abc123", developer_id="d2")
    assert f["is_fork"]
    assert f["forked_from"] == "abc123"

def test_export():
    p = {"share_id": "abc", "config": {"timeout_ms": 5000}}
    e = export_playground(playground=p)
    assert e["exportable"]
