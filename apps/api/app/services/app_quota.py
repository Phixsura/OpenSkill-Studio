"""App quota management — enforce resource limits per developer/tier.

Tracks and enforces quotas for:
- Max apps per developer
- Max versions per app
- Max installations per org
- Max API keys per app
- Max secrets per installation
"""

from dataclasses import dataclass


@dataclass
class QuotaLimits:
    max_apps: int = 10
    max_versions_per_app: int = 50
    max_installations_per_org: int = 20
    max_api_keys_per_app: int = 5
    max_secrets_per_installation: int = 20
    max_event_subscriptions: int = 50
    max_automation_rules: int = 25
    max_ui_extensions: int = 10


TIER_LIMITS = {
    "free": QuotaLimits(max_apps=3, max_versions_per_app=10, max_api_keys_per_app=2),
    "standard": QuotaLimits(),
    "premium": QuotaLimits(max_apps=50, max_versions_per_app=200, max_api_keys_per_app=20),
    "enterprise": QuotaLimits(max_apps=500, max_versions_per_app=1000, max_api_keys_per_app=100,
                              max_installations_per_org=100, max_secrets_per_installation=100),
}


def get_limits(tier: str = "standard") -> QuotaLimits:
    return TIER_LIMITS.get(tier, TIER_LIMITS["standard"])


def check_quota(*, current: int, limit: int, resource: str) -> dict:
    """Check if a resource quota would be exceeded."""
    return {
        "allowed": current < limit,
        "current": current,
        "limit": limit,
        "resource": resource,
        "remaining": max(0, limit - current),
    }
