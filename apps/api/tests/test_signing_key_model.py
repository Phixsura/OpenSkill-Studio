"""AppSigningKey model tests."""

import pytest
from app.models.developer import AppSigningKey

def test_has_public_key():
    cols = {c.name for c in AppSigningKey.__table__.columns}
    assert "public_key" in cols

def test_has_fingerprint():
    cols = {c.name for c in AppSigningKey.__table__.columns}
    assert "fingerprint" in cols

def test_has_developer_id_fk():
    col = AppSigningKey.__table__.columns["developer_id"]
    assert len(col.foreign_keys) > 0

def test_has_name():
    cols = {c.name for c in AppSigningKey.__table__.columns}
    assert "name" in cols

def test_public_key_not_nullable():
    col = AppSigningKey.__table__.columns["public_key"]
    assert not col.nullable
