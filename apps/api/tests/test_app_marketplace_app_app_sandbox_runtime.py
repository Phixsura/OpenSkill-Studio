from app.services.app_marketplace_app_app_sandbox_runtime import create_sandbox, list_runtimes

def test_create():
    r = create_sandbox(app_id="app1", runtime="python312", memory_mb=512)
    assert r["sandbox_id"].startswith("sbx_")
    assert r["runtime"] == "python312"
    assert r["memory_mb"] == 512
    assert not r["network_enabled"]
    assert r["fs_readonly"]

def test_runtimes():
    r = list_runtimes()
    assert len(r) == 6
    assert any(x["id"] == "node20" for x in r)
    assert any(x["id"] == "python312" for x in r)
