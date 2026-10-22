"""540th commit — verify 100 backend services."""

import importlib
import os
import pytest

SERVICES_DIR = os.path.join(os.path.dirname(__file__), "..", "app", "services")

def test_100_service_files():
    """We should have ~100 service files."""
    py_files = [f for f in os.listdir(SERVICES_DIR) if f.endswith(".py") and f != "__init__.py"]
    assert len(py_files) >= 95, f"Only {len(py_files)} service files"

def test_all_importable():
    """Every service file should be importable."""
    py_files = [f[:-3] for f in os.listdir(SERVICES_DIR) if f.endswith(".py") and f != "__init__.py"]
    for mod_name in py_files:
        mod = importlib.import_module(f"app.services.{mod_name}")
        assert mod is not None, f"Failed to import app.services.{mod_name}"
