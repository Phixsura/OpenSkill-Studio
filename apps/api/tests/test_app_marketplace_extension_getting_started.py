from app.services.app_marketplace_extension_getting_started import ExtensionGettingStartedService


def test_initialize():
    svc = ExtensionGettingStartedService()
    items = svc.initialize("dev-1")
    assert len(items) == 8
    assert items[0].item_id == "account"


def test_complete_item():
    svc = ExtensionGettingStartedService()
    svc.initialize("dev-1")
    assert svc.complete_item("dev-1", "account") is True
    progress = svc.get_progress("dev-1")
    assert progress["completed"] == 1
    assert progress["percent"] == 12


def test_progress_next_step():
    svc = ExtensionGettingStartedService()
    svc.initialize("dev-1")
    svc.complete_item("dev-1", "account")
    progress = svc.get_progress("dev-1")
    assert progress["next_step"] == "Install CLI Tools"


def test_all_done():
    svc = ExtensionGettingStartedService()
    svc.initialize("dev-1")
    for iid, _, _, _, _ in [("account", "", "", "", 0), ("install_cli", "", "", "", 0),
                             ("scaffold", "", "", "", 0), ("manifest", "", "", "", 0),
                             ("local_dev", "", "", "", 0), ("write_tests", "", "", "", 0),
                             ("submit", "", "", "", 0), ("publish", "", "", "", 0)]:
        svc.complete_item("dev-1", iid)
    progress = svc.get_progress("dev-1")
    assert progress["all_done"] is True
    assert progress["percent"] == 100
