"""Access Control — role-based access control for marketplace operations.

Defines roles (viewer, developer, reviewer, admin) with granular
action permissions for extension marketplace operations.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum


class Role(str, Enum):
    VIEWER = "viewer"
    DEVELOPER = "developer"
    REVIEWER = "reviewer"
    ADMIN = "admin"


class Action(str, Enum):
    # Extension actions
    VIEW_EXTENSION = "extension.view"
    CREATE_EXTENSION = "extension.create"
    PUBLISH_EXTENSION = "extension.publish"
    DEPRECATE_EXTENSION = "extension.deprecate"
    # Install actions
    INSTALL = "install.create"
    UNINSTALL = "install.delete"
    CONFIGURE = "install.configure"
    # Review actions
    SUBMIT_REVIEW = "review.create"
    FLAG_REVIEW = "review.flag"
    MODERATE_REVIEW = "review.moderate"
    # Admin actions
    APPROVE_EXTENSION = "admin.approve"
    REJECT_EXTENSION = "admin.reject"
    SUSPEND_EXTENSION = "admin.suspend"
    MANAGE_USERS = "admin.manage_users"
    VIEW_AUDIT_LOG = "admin.audit_log"


# Role -> set of allowed actions
ROLE_PERMISSIONS: dict[Role, set[Action]] = {
    Role.VIEWER: {
        Action.VIEW_EXTENSION, Action.INSTALL, Action.UNINSTALL,
        Action.SUBMIT_REVIEW,
    },
    Role.DEVELOPER: {
        Action.VIEW_EXTENSION, Action.CREATE_EXTENSION,
        Action.PUBLISH_EXTENSION, Action.DEPRECATE_EXTENSION,
        Action.INSTALL, Action.UNINSTALL, Action.CONFIGURE,
        Action.SUBMIT_REVIEW,
    },
    Role.REVIEWER: {
        Action.VIEW_EXTENSION, Action.INSTALL, Action.SUBMIT_REVIEW,
        Action.FLAG_REVIEW, Action.MODERATE_REVIEW,
        Action.APPROVE_EXTENSION, Action.REJECT_EXTENSION,
    },
    Role.ADMIN: set(Action),  # all actions
}


class AccessControl:
    """Role-based access control for marketplace operations."""

    def __init__(self):
        self._user_roles: dict[str, dict[str, Role]] = {}  # user -> {org: role}
        self._overrides: dict[str, set[Action]] = {}  # user -> extra actions

    def assign_role(self, user_id: str, org_id: str, role: Role) -> None:
        self._user_roles.setdefault(user_id, {})[org_id] = role

    def get_role(self, user_id: str, org_id: str) -> Role | None:
        return self._user_roles.get(user_id, {}).get(org_id)

    def grant_override(self, user_id: str, action: Action) -> None:
        """Grant a specific action override regardless of role."""
        self._overrides.setdefault(user_id, set()).add(action)

    def revoke_override(self, user_id: str, action: Action) -> None:
        overrides = self._overrides.get(user_id, set())
        overrides.discard(action)

    def can(self, user_id: str, org_id: str, action: Action) -> bool:
        """Check if user can perform action in org context."""
        # Check overrides first
        if action in self._overrides.get(user_id, set()):
            return True
        role = self.get_role(user_id, org_id)
        if not role:
            return False
        return action in ROLE_PERMISSIONS.get(role, set())

    def get_permissions(self, user_id: str, org_id: str) -> list[str]:
        """Get all allowed actions for a user in an org."""
        role = self.get_role(user_id, org_id)
        base = ROLE_PERMISSIONS.get(role, set()) if role else set()
        overrides = self._overrides.get(user_id, set())
        return sorted(a.value for a in base | overrides)

    def require(self, user_id: str, org_id: str, action: Action) -> None:
        """Raise if user lacks permission."""
        if not self.can(user_id, org_id, action):
            raise PermissionError(
                f"User {user_id} lacks {action.value} permission in org {org_id}"
            )
