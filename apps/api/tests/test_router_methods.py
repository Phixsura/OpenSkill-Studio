"""Router HTTP method verification."""

import pytest
from app.api.v1.endpoints import (
    developer_accounts, developer_apps, app_installations,
    app_marketplace, oauth,
)

def _get_methods(module):
    methods = set()
    for route in module.router.routes:
        if hasattr(route, "methods"):
            methods.update(route.methods)
    return methods

def test_developer_accounts_has_get_post():
    methods = _get_methods(developer_accounts)
    assert "GET" in methods
    assert "POST" in methods

def test_developer_apps_has_crud():
    methods = _get_methods(developer_apps)
    assert "GET" in methods
    assert "POST" in methods

def test_installations_has_get():
    methods = _get_methods(app_installations)
    assert "GET" in methods

def test_marketplace_has_get():
    methods = _get_methods(app_marketplace)
    assert "GET" in methods

def test_oauth_has_post():
    methods = _get_methods(oauth)
    assert "POST" in methods

ROUTERS_WITH_GET = [developer_accounts, developer_apps, app_installations, app_marketplace]

@pytest.mark.parametrize("module", ROUTERS_WITH_GET, ids=lambda m: m.__name__)
def test_all_have_get(module):
    assert "GET" in _get_methods(module)
