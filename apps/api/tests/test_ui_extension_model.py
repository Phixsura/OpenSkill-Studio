"""AppUiExtension model tests."""

import pytest
from app.models.developer import AppUiExtension

def test_has_surface():
    cols = {c.name for c in AppUiExtension.__table__.columns}
    assert "surface" in cols

def test_has_title():
    cols = {c.name for c in AppUiExtension.__table__.columns}
    assert "title" in cols

def test_has_entry_path():
    cols = {c.name for c in AppUiExtension.__table__.columns}
    assert "entry_path" in cols

def test_has_app_id_fk():
    col = AppUiExtension.__table__.columns["app_id"]
    assert len(col.foreign_keys) > 0

def test_surface_not_nullable():
    col = AppUiExtension.__table__.columns["surface"]
    assert not col.nullable
