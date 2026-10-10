"""Integration fabric models (ADR-018). Importing this module registers all
intg_* tables on the shared SQLAlchemy Base metadata."""

from app.integrations.models.connection import (  # noqa: F401
    CONNECTION_STATUSES,
    CONNECTION_TRANSITIONS,
    CREDENTIAL_KINDS,
    DEGRADE_AFTER_FAILURES,
    SCHEDULABLE_STATUSES,
    IntegrationConnection,
    IntegrationConnectionCredential,
)
from app.integrations.models.events import (  # noqa: F401
    DELIVERY_STATUSES,
    EVENT_NAMESPACE,
    INTERNAL_EVENT_PREFIX,
    MAX_ATTEMPTS,
    RETRY_OFFSETS_S,
    DeliveryAttempt,
    EventDelivery,
    IntegrationEvent,
)
from app.integrations.models.provider import (  # noqa: F401
    AUTH_MODES,
    PROVIDER_CATEGORIES,
    IntegrationProvider,
)
