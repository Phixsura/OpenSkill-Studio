"""Verify all async service functions have proper signatures."""

import pytest
import asyncio
from app.services.developer import (
    create_developer_account, get_developer_account, get_developer_account_by_user,
    list_developer_accounts, update_developer_account, create_app, get_app,
    list_apps, update_app, transition_app_status, create_app_version,
    get_app_version, list_app_versions, review_app_version,
    install_app, get_installation, list_installations, uninstall_app,
    update_installation, create_api_key, authenticate_api_key, list_api_keys,
    revoke_api_key, create_event_subscription, list_event_subscriptions,
    delete_event_subscription, create_automation_rule, list_automation_rules,
    get_automation_rule, update_automation_rule, delete_automation_rule,
    set_secret, get_decrypted_secrets, list_secret_metadata, delete_secret,
    register_signing_key, list_signing_keys, submit_for_review,
    list_review_submissions, decide_review, revoke_app, log_sandbox_execution,
    list_sandbox_executions,
)

ALL_FUNCS = [
    create_developer_account, get_developer_account, get_developer_account_by_user,
    list_developer_accounts, update_developer_account, create_app, get_app,
    list_apps, update_app, transition_app_status, create_app_version,
    get_app_version, list_app_versions, review_app_version,
    install_app, get_installation, list_installations, uninstall_app,
    update_installation, create_api_key, authenticate_api_key, list_api_keys,
    revoke_api_key, create_event_subscription, list_event_subscriptions,
    delete_event_subscription, create_automation_rule, list_automation_rules,
    get_automation_rule, update_automation_rule, delete_automation_rule,
    set_secret, get_decrypted_secrets, list_secret_metadata, delete_secret,
    register_signing_key, list_signing_keys, submit_for_review,
    list_review_submissions, decide_review, revoke_app, log_sandbox_execution,
    list_sandbox_executions,
]

@pytest.mark.parametrize("fn", ALL_FUNCS, ids=lambda f: f.__name__)
def test_is_async(fn):
    assert asyncio.iscoroutinefunction(fn)

def test_total_functions():
    assert len(ALL_FUNCS) == 43
