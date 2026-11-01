from app.services.app_marketplace_app_app_app_app_app_app_app_content_ver import (
    create_revision, diff_revisions, revision_history,
)

def test_revision():
    r = create_revision("doc_1", "Hello world", "alice", "Initial")
    assert len(r["revision"]) == 10
    assert r["size"] == 11

def test_diff():
    d = diff_revisions("line1\nline2\nline3", "line1\nchanged\nline3\nnew")
    assert d["changed_lines"] == 1
    assert d["added_lines"] == 1
    assert d["total_changes"] == 2

def test_history():
    revs = [
        create_revision("d", "v1", "alice"),
        create_revision("d", "v2", "bob"),
        create_revision("d", "v3", "alice"),
    ]
    h = revision_history(revs)
    assert h["total"] == 3
    assert h["author_count"] == 2
