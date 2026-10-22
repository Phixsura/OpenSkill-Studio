"""DeveloperApp model detailed tests."""

import pytest
from app.models.developer import DeveloperApp

REQUIRED = ["id", "developer_id", "name", "slug", "category", "status", "visibility", "oauth_client_id", "created_at"]

@pytest.mark.parametrize("col", REQUIRED)
def test_required(col):
    assert col in {c.name for c in DeveloperApp.__table__.columns}

def test_developer_id_fk():
    assert len(DeveloperApp.__table__.columns["developer_id"].foreign_keys) > 0

def test_name_not_nullable():
    assert not DeveloperApp.__table__.columns["name"].nullable

def test_slug_not_nullable():
    assert not DeveloperApp.__table__.columns["slug"].nullable

def test_has_description():
    assert "description" in {c.name for c in DeveloperApp.__table__.columns}

def test_has_webhook_url():
    assert "webhook_url" in {c.name for c in DeveloperApp.__table__.columns}
