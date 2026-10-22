from __future__ import annotations

"""OpenSkill Platform SDK for Python.

Build apps, connectors, and extensions for OpenSkill Studio.

Usage::

    from openskill_sdk import OpenSkillClient

    client = OpenSkillClient(api_key="osk_app_...")
    account = await client.developer.get_me()
    apps = await client.apps.list()
"""

from openskill_sdk.client import OpenSkillClient
from openskill_sdk.errors import ApiError, AuthError, NotFoundError, OpenSkillError
from openskill_sdk.adapter import (
    Capability,
    EcosystemSourceAdapter,
    HealthCheck,
    ProviderAdapter,
    SourceRecord,
)

__all__ = [
    "OpenSkillClient",
    "OpenSkillError",
    "ApiError",
    "AuthError",
    "NotFoundError",
    "ProviderAdapter",
    "EcosystemSourceAdapter",
    "Capability",
    "HealthCheck",
    "SourceRecord",
]

__version__ = "0.1.0"
