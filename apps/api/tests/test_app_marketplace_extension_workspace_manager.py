from app.services.app_marketplace_extension_workspace_manager import (
    WorkspaceManagerService, WorkspaceStatus,
)


def test_create_workspace():
    svc = WorkspaceManagerService()
    ws = svc.create("ext-1", "dev-1", "My Workspace")
    assert ws.status == WorkspaceStatus.ACTIVE
    assert ws.owner_id == "dev-1"


def test_add_and_get_file():
    svc = WorkspaceManagerService()
    ws = svc.create("ext-1", "dev-1", "WS")
    svc.add_file(ws.workspace_id, "src/index.ts", "export default {}", caller_id="dev-1")
    content = svc.get_file(ws.workspace_id, "src/index.ts", "dev-1")
    assert content == "export default {}"


def test_unauthorized_add():
    svc = WorkspaceManagerService()
    ws = svc.create("ext-1", "dev-1", "WS")
    result = svc.add_file(ws.workspace_id, "hack.ts", "evil", caller_id="attacker")
    assert isinstance(result, dict) and "error" in result


def test_path_traversal_blocked():
    svc = WorkspaceManagerService()
    ws = svc.create("ext-1", "dev-1", "WS")
    result = svc.add_file(ws.workspace_id, "../etc/passwd", "data", caller_id="dev-1")
    assert isinstance(result, dict) and "traversal" in result["error"]


def test_language_detection():
    svc = WorkspaceManagerService()
    ws = svc.create("ext-1", "dev-1", "WS")
    svc.add_file(ws.workspace_id, "main.py", "print('hi')", caller_id="dev-1")
    files = svc.list_files(ws.workspace_id)
    assert files[0]["language"] == "python"


def test_collaborator():
    svc = WorkspaceManagerService()
    ws = svc.create("ext-1", "dev-1", "WS")
    svc.add_collaborator(ws.workspace_id, "dev-2", "dev-1")
    svc.add_file(ws.workspace_id, "collab.ts", "// by dev-2", caller_id="dev-2")
    assert svc.get_file(ws.workspace_id, "collab.ts", "dev-2") is not None


def test_only_owner_adds_collaborator():
    svc = WorkspaceManagerService()
    ws = svc.create("ext-1", "dev-1", "WS")
    assert svc.add_collaborator(ws.workspace_id, "dev-2", "dev-3") is False


def test_archive():
    svc = WorkspaceManagerService()
    ws = svc.create("ext-1", "dev-1", "WS")
    assert svc.archive(ws.workspace_id, "dev-1") is True
    assert ws.status == WorkspaceStatus.ARCHIVED


def test_list_workspaces():
    svc = WorkspaceManagerService()
    svc.create("ext-1", "dev-1", "WS1")
    ws2 = svc.create("ext-2", "dev-2", "WS2")
    svc.add_collaborator(ws2.workspace_id, "dev-1", "dev-2")
    listed = svc.list_workspaces("dev-1")
    assert len(listed) == 2  # own + collaborator
