"""Migration file verification."""

import os
import pytest

MIGRATION_DIR = os.path.join(os.path.dirname(__file__), "..", "migrations", "versions")

def test_devplatform01_exists():
    files = os.listdir(MIGRATION_DIR)
    matches = [f for f in files if "devplatform01" in f]
    assert len(matches) == 1

def test_devplatform02_exists():
    files = os.listdir(MIGRATION_DIR)
    matches = [f for f in files if "devplatform02" in f]
    assert len(matches) == 1

def test_migration_files_are_python():
    files = os.listdir(MIGRATION_DIR)
    dev_files = [f for f in files if "devplatform" in f]
    for f in dev_files:
        assert f.endswith(".py"), f"{f} is not a Python file"

def test_migrations_importable():
    """Alembic migrations should be syntactically valid Python."""
    import importlib.util
    files = os.listdir(MIGRATION_DIR)
    for f in [f for f in files if "devplatform" in f and f.endswith(".py")]:
        path = os.path.join(MIGRATION_DIR, f)
        spec = importlib.util.spec_from_file_location(f, path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        assert hasattr(mod, "upgrade")
        assert hasattr(mod, "downgrade")
