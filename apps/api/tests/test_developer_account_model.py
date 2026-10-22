"""DeveloperAccount model tests."""

import pytest
from app.models.developer import DeveloperAccount

REQUIRED = ["id", "owner_user_id", "display_name", "slug", "support_email", "status", "created_at"]

@pytest.mark.parametrize("col", REQUIRED)
def test_required(col):
    assert col in {c.name for c in DeveloperAccount.__table__.columns}

def test_slug_unique():
    col = DeveloperAccount.__table__.columns["slug"]
    assert col.unique or any("slug" in [c.name for c in idx.columns] for idx in DeveloperAccount.__table__.indexes)

def test_display_name_not_nullable():
    assert not DeveloperAccount.__table__.columns["display_name"].nullable

def test_slug_not_nullable():
    assert not DeveloperAccount.__table__.columns["slug"].nullable

def test_has_updated_at():
    assert "updated_at" in {c.name for c in DeveloperAccount.__table__.columns}

def test_has_website_url():
    assert "website_url" in {c.name for c in DeveloperAccount.__table__.columns}
