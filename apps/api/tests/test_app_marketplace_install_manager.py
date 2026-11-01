from app.services.app_marketplace_install_manager import InstallManager, InstallState


def test_install_and_list():
    im = InstallManager()
    inst, msg = im.install("org-1", "ext-1", "1.0.0", "admin")
    assert inst is not None
    assert inst.state == InstallState.ENABLED
    installed = im.list_installed("org-1")
    assert len(installed) == 1


def test_duplicate_install():
    im = InstallManager()
    im.install("org-2", "ext-2", "1.0.0", "admin")
    inst, msg = im.install("org-2", "ext-2", "1.0.0", "admin")
    assert inst is None
    assert "already installed" in msg


def test_uninstall():
    im = InstallManager()
    im.install("org-3", "ext-3", "1.0.0", "admin")
    assert im.uninstall("org-3", "ext-3") is True
    assert im.list_installed("org-3") == []


def test_enable_disable():
    im = InstallManager()
    im.install("org-4", "ext-4", "1.0.0", "admin")
    assert im.disable("org-4", "ext-4") is True
    assert im.get_installation("org-4", "ext-4").state == InstallState.DISABLED
    assert im.enable("org-4", "ext-4") is True
    assert im.get_installation("org-4", "ext-4").state == InstallState.ENABLED


def test_upgrade():
    im = InstallManager()
    im.install("org-5", "ext-5", "1.0.0", "admin")
    ok, msg = im.upgrade("org-5", "ext-5", "2.0.0")
    assert ok is True
    assert "1.0.0 -> 2.0.0" in msg
    assert im.get_installation("org-5", "ext-5").version == "2.0.0"


def test_rollback():
    im = InstallManager()
    im.install("org-6", "ext-6", "1.0.0", "admin")
    im.upgrade("org-6", "ext-6", "2.0.0")
    ok, msg = im.rollback("org-6", "ext-6")
    assert ok is True
    assert im.get_installation("org-6", "ext-6").version == "1.0.0"


def test_rollback_no_previous():
    im = InstallManager()
    im.install("org-7", "ext-7", "1.0.0", "admin")
    ok, msg = im.rollback("org-7", "ext-7")
    assert ok is False
