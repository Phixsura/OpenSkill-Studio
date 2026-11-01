from app.services.app_developer_agreement import accept_agreement, has_accepted, needs_reaccept, CURRENT_TOS_VERSION

def test_accept():
    accept_agreement("d1")
    assert has_accepted("d1") is True

def test_not_accepted():
    assert has_accepted("unknown") is False

def test_needs_reaccept_new():
    assert needs_reaccept("brand_new") is True

def test_needs_reaccept_current():
    accept_agreement("d2")
    assert needs_reaccept("d2") is False

def test_needs_reaccept_old_version():
    accept_agreement("d3", tos_version="2020-01-01")
    assert needs_reaccept("d3") is True
