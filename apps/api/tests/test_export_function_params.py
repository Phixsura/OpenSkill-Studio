"""Export function parameter tests."""

import inspect
import pytest
from app.services.app_export import export_app_config, export_installation_config

def test_export_app_has_app_id():
    assert "app_id" in inspect.signature(export_app_config).parameters

def test_export_app_has_db():
    assert "db" in inspect.signature(export_app_config).parameters

def test_export_installation_has_installation_id():
    assert "installation_id" in inspect.signature(export_installation_config).parameters

def test_export_installation_has_db():
    assert "db" in inspect.signature(export_installation_config).parameters

def test_export_app_return_hint():
    hints = inspect.get_annotations(export_app_config)
    assert "return" in hints

def test_export_installation_return_hint():
    hints = inspect.get_annotations(export_installation_config)
    assert "return" in hints
