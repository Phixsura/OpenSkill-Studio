"""AppInstallation model detailed tests."""

import pytest
from app.models.developer import AppInstallation

REQUIRED = ["id", "app_id", "app_version_id", "org_id", "installed_by", "status", "created_at"]

@pytest.mark.parametrize("col", REQUIRED)
def test_required(col):
    assert col in {c.name for c in AppInstallation.__table__.columns}

def test_app_id_fk():
    assert len(AppInstallation.__table__.columns["app_id"].foreign_keys) > 0

def test_org_id_not_nullable():
    assert not AppInstallation.__table__.columns["org_id"].nullable

def test_status_not_nullable():
    assert not AppInstallation.__table__.columns["status"].nullable

def test_has_config_or_settings():
    cols = {c.name for c in AppInstallation.__table__.columns}
    assert "config" in cols or "settings" in cols or "granted_permissions" in cols
