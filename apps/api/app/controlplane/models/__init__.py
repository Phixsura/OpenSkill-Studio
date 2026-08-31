"""Control-plane SQLAlchemy models (all tables prefixed cp_).

NOT imported from app.models.__init__ (that would be circular: cp models
import app.models.base, whose parent package init would re-import cp).
Alembic's env.py and app startup import this package explicitly instead.
"""

from app.controlplane.models.audit import CommercialAuditEvent  # noqa: F401
from app.controlplane.models.outbox import OutboxMessage  # noqa: F401
from app.controlplane.models.tenant import (  # noqa: F401
    PlatformRoleAssignment,
    SupportImpersonationGrant,
    TenantAccount,
    TenantAccountType,
    TenantMember,
    TenantStatus,
)
