"""AppSecret encrypted_value column tests."""

import pytest
from sqlalchemy import LargeBinary, String, Text
from app.models.developer import AppSecret

def test_has_encrypted_value():
    cols = {c.name for c in AppSecret.__table__.columns}
    assert "encrypted_value" in cols

def test_has_key():
    cols = {c.name for c in AppSecret.__table__.columns}
    assert "key" in cols

def test_has_installation_id():
    cols = {c.name for c in AppSecret.__table__.columns}
    assert "installation_id" in cols

def test_encrypted_value_not_nullable():
    col = AppSecret.__table__.columns["encrypted_value"]
    assert not col.nullable

def test_key_not_nullable():
    col = AppSecret.__table__.columns["key"]
    assert not col.nullable
