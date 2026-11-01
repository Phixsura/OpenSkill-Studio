from app.services.app_marketplace_app_app_app_app_release_manager import create_release, advance_stage

def test_create():
    r = create_release(app_id="a1", version="3.0.0", changelog="Big update", breaking=True)
    assert r["release_id"].startswith("rel_")
    assert r["stage"] == "draft"
    assert r["breaking"]

def test_advance():
    r = advance_stage(current_stage="draft")
    assert r["current"] == "testing"
    assert not r["is_final"]

def test_advance_to_published():
    r = advance_stage(current_stage="approved")
    assert r["current"] == "published"
    assert r["is_final"]

def test_already_final():
    r = advance_stage(current_stage="published")
    assert "error" in r
