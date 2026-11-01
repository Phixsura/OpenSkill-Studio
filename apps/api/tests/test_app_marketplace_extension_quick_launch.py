from app.services.app_marketplace_extension_quick_launch import (
    ExtensionQuickLaunchService, LaunchStatus,
)


def test_launch():
    svc = ExtensionQuickLaunchService()
    ql = svc.launch("slack-bot", "my-bot", "node20")
    assert ql.status == LaunchStatus.INITIALIZING
    assert ql.progress_pct == 0


def test_advance_to_live():
    svc = ExtensionQuickLaunchService()
    ql = svc.launch("api-connector", "my-api")
    for _ in range(4):
        svc.advance(ql.launch_id)
    assert ql.status == LaunchStatus.LIVE
    assert "preview.openskill.dev" in ql.preview_url
    assert ql.progress_pct == 100


def test_fail():
    svc = ExtensionQuickLaunchService()
    ql = svc.launch("template", "ext")
    svc.fail(ql.launch_id, "Build error")
    assert ql.status == LaunchStatus.FAILED
    assert ql.error == "Build error"


def test_progress():
    svc = ExtensionQuickLaunchService()
    ql = svc.launch("t", "e")
    svc.advance(ql.launch_id)
    svc.advance(ql.launch_id)
    assert ql.progress_pct == 50
