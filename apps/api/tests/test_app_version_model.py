"""AppVersion model tests."""

import pytest
from sqlalchemy.dialects.postgresql import JSONB
from app.models.developer import AppVersion

REQUIRED = ["id", "app_id", "version", "manifest", "content_hash", "review_status", "created_at"]

@pytest.mark.parametrize("col", REQUIRED)
def test_required(col):
    assert col in {c.name for c in AppVersion.__table__.columns}

def test_app_id_fk():
    assert len(AppVersion.__table__.columns["app_id"].foreign_keys) > 0

def test_manifest_is_jsonb():
    col = AppVersion.__table__.columns["manifest"]
    assert isinstance(col.type, JSONB) or "json" in str(col.type).lower()

def test_version_not_nullable():
    assert not AppVersion.__table__.columns["version"].nullable

def test_content_hash_not_nullable():
    assert not AppVersion.__table__.columns["content_hash"].nullable
