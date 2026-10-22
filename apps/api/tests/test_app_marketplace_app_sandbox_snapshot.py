from app.services.app_marketplace_app_sandbox_snapshot import create_snapshot, list_snapshots, restore_snapshot

def test_create():
    s = create_snapshot(sandbox_id="sb1", name="before-deploy", filesystem={"files": 5}, config={"debug": True})
    assert s["snapshot_id"].startswith("snap_")
    assert s["filesystem_files"] == 5

def test_list():
    snaps = [{"created_at": "2026-01-01"}, {"created_at": "2026-06-01"}, {"created_at": "2026-03-01"}]
    r = list_snapshots(snapshots=snaps, limit=2)
    assert len(r) == 2
    assert r[0]["created_at"] == "2026-06-01"

def test_restore():
    r = restore_snapshot(snapshot={"snapshot_id": "snap_abc123"})
    assert r["status"] == "restored"
