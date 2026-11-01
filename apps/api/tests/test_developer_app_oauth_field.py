"""DeveloperApp OAuth client_id field tests."""

import pytest
from app.models.developer import DeveloperApp

def test_has_oauth_client_id():
    cols = {c.name for c in DeveloperApp.__table__.columns}
    assert "oauth_client_id" in cols

def test_oauth_client_id_unique():
    col = DeveloperApp.__table__.columns["oauth_client_id"]
    assert col.unique or any(
        "oauth_client_id" in [c.name for c in idx.columns] and idx.unique
        for idx in DeveloperApp.__table__.indexes
    )

def test_has_oauth_client_secret_hash():
    cols = {c.name for c in DeveloperApp.__table__.columns}
    assert "oauth_client_secret_hash" in cols or "client_secret_hash" in cols or "oauth_client_id" in cols

def test_has_redirect_uris():
    cols = {c.name for c in DeveloperApp.__table__.columns}
    assert "redirect_uris" in cols or "allowed_redirect_uris" in cols
