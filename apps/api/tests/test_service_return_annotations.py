"""Service functions — return type annotations exist."""

import inspect
import pytest
from app.services.developer import (
    create_developer_account, get_developer_account, list_developer_accounts,
    create_app, get_app, list_apps,
    create_app_version, get_app_version, list_app_versions,
    install_app, get_installation, list_installations,
    create_api_key, list_api_keys,
)

FUNCS = [
    create_developer_account, get_developer_account, list_developer_accounts,
    create_app, get_app, list_apps,
    create_app_version, get_app_version, list_app_versions,
    install_app, get_installation, list_installations,
    create_api_key, list_api_keys,
]

@pytest.mark.parametrize("func", FUNCS, ids=lambda f: f.__name__)
def test_has_return_annotation(func):
    hints = inspect.get_annotations(func)
    assert "return" in hints, f"{func.__name__} missing return annotation"
