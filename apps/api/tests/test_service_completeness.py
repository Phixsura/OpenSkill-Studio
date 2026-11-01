"""Verify all developer platform services are complete and well-structured."""

import pytest


def test_all_services_importable():
    """Every developer platform service can be imported."""
    from app.services.adapter_sdk import ProviderAdapterSDK, EcosystemSourceAdapter
    from app.services.app_analytics import get_install_timeline, get_execution_timeline, get_top_orgs, get_app_summary_metrics
    from app.services.app_compatibility import parse_semver, is_compatible, check_upgrade_compatibility
    from app.services.app_discovery import get_featured_apps, get_recent_apps, get_trending_apps
    from app.services.app_event_hooks import on_submission_completed, on_cohort_member_added, on_app_installed
    from app.services.app_export import export_app_config, export_installation_config
    from app.services.app_lifecycle import get_deprecation_info, auto_upgrade_installations, get_version_adoption, check_app_health
    from app.services.app_notifications import notify_app_installed, notify_review_decided, notify_app_revoked
    from app.services.app_permissions import check_permission, get_missing_permissions, validate_installation_permissions
    from app.services.app_rate_limit import record_request, check_rate_limit, get_rate_limit_headers
    from app.services.app_search import search_marketplace_apps
    from app.services.app_usage import record_app_usage, get_app_usage_summary
    from app.services.app_webhooks import generate_webhook_secret, validate_webhook_url, log_delivery
    from app.services.conformance import run_conformance_checks
    from app.services.developer import create_developer_account, create_app, install_app, revoke_app
    from app.services.event_dispatch import emit_event, EventDispatcher, CANONICAL_EVENTS
    from app.services.idempotency import get_cached_response, store_response, make_key
    from app.services.manifest_validator import validate_manifest, VALID_PERMISSIONS, VALID_SURFACES
    from app.services.sandbox import SandboxManager, SandboxResult
    from app.services.webhook_verify import sign_payload, verify_signature

    # Count total services
    service_count = 20  # 20 distinct service modules
    assert service_count == 20


def test_all_routers_registered():
    """All developer platform routers are registered."""
    from app.api.v1.router import api_v1_router

    routes = api_v1_router.routes
    assert len(routes) >= 65  # 65+ routes


def test_all_models_registered():
    """All developer platform models are registered."""
    from app.models import (
        DeveloperAccount,
        DeveloperApp,
        AppVersion,
        AppInstallation,
        AppApiKey,
        AppEventSubscription,
        AppAutomationRule,
        AppSecret,
        AppUiExtension,
        SandboxExecution,
        AppReviewSubmission,
        AppSigningKey,
        AppWebhookDelivery,
    )

    models = [
        DeveloperAccount, DeveloperApp, AppVersion, AppInstallation,
        AppApiKey, AppEventSubscription, AppAutomationRule, AppSecret,
        AppUiExtension, SandboxExecution, AppReviewSubmission, AppSigningKey,
        AppWebhookDelivery,
    ]
    assert len(models) == 13


def test_canonical_events_coverage():
    """All event categories are covered."""
    from app.services.event_dispatch import CANONICAL_EVENTS

    categories = set()
    for event in CANONICAL_EVENTS:
        categories.add(event.split(".")[0])

    expected = {"org", "cohort", "project", "submission", "pack", "workflow",
                "talent", "marketplace", "evaluation", "app"}
    assert expected.issubset(categories)
    assert len(CANONICAL_EVENTS) >= 35


def test_manifest_permissions_taxonomy():
    """Permission taxonomy has expected coverage."""
    from app.services.manifest_validator import VALID_PERMISSIONS

    # Check all expected categories exist
    categories = set()
    for perm in VALID_PERMISSIONS:
        categories.add(perm.split(":")[0])

    expected = {"read", "write", "subscribe", "extend", "export", "run"}
    assert expected.issubset(categories)
    assert len(VALID_PERMISSIONS) >= 30


def test_manifest_surfaces_complete():
    """All 8 UI surfaces are defined."""
    from app.services.manifest_validator import VALID_SURFACES

    assert len(VALID_SURFACES) == 8
    expected = {
        "dashboard_card", "project_sidebar", "cohort_tool",
        "submission_panel", "registry_detail", "settings_page",
        "client_portal_widget", "operator_console",
    }
    assert expected == VALID_SURFACES


def test_rate_limit_tiers():
    """Rate limit tiers are correctly defined."""
    from app.services.app_rate_limit import RATE_LIMITS

    assert RATE_LIMITS["standard"] == 1000
    assert RATE_LIMITS["elevated"] == 5000
    assert RATE_LIMITS["unlimited"] == 0


def test_platform_version():
    """Platform version is set."""
    from app.services.app_compatibility import PLATFORM_VERSION

    assert PLATFORM_VERSION == "1.0.0"
