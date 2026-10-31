from app.services.app_marketplace_app_app_app_app_app_app_app_api_sandbox import ApiSandbox

def test_sandbox():
    sb = ApiSandbox()
    s = sb.create(owner="alice", name="test-env")
    assert s["status"] == "ready"
    assert "sbx_" in s["id"]
    sb.use(s["id"])
    sb.use(s["id"])
    sandboxes = sb.list_sandboxes("alice")
    assert len(sandboxes) == 1
    assert sandboxes[0]["request_count"] == 2
    sb.destroy(s["id"])
    assert len(sb.list_sandboxes("alice")) == 0
