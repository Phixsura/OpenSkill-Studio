"""Isolation Manager — manage isolation boundaries between extension sandboxes.

Enforces namespace isolation, shared resource boundaries, inter-sandbox
communication policies, and tenant separation for multi-tenant deployments.
"""
from __future__ import annotations
import secrets
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum


class IsolationLevel(str, Enum):
    SHARED = "shared"         # shared namespace, shared resources
    NAMESPACE = "namespace"   # separate namespace, shared resources  
    FULL = "full"             # separate namespace, separate resources


class CommunicationPolicy(str, Enum):
    DENY_ALL = "deny_all"
    ALLOW_SAME_TENANT = "allow_same_tenant"
    ALLOW_EXPLICIT = "allow_explicit"


@dataclass
class SandboxBoundary:
    sandbox_id: str
    tenant_id: str
    isolation_level: IsolationLevel
    namespace: str
    comm_policy: CommunicationPolicy = CommunicationPolicy.DENY_ALL
    allowed_peers: set[str] = field(default_factory=set)
    shared_volumes: list[str] = field(default_factory=list)


class IsolationManagerService:
    """Enforces isolation boundaries between extension sandboxes."""

    def __init__(self):
        self._boundaries: dict[str, SandboxBoundary] = {}

    def register(self, sandbox_id: str, tenant_id: str,
                 isolation_level: IsolationLevel = IsolationLevel.FULL,
                 comm_policy: CommunicationPolicy = CommunicationPolicy.DENY_ALL) -> SandboxBoundary:
        if sandbox_id in self._boundaries:
            raise ValueError("Sandbox already registered")
        namespace = f"ns_{tenant_id}_{secrets.token_hex(4)}"
        boundary = SandboxBoundary(
            sandbox_id=sandbox_id, tenant_id=tenant_id,
            isolation_level=isolation_level, namespace=namespace,
            comm_policy=comm_policy,
        )
        self._boundaries[sandbox_id] = boundary
        return boundary

    def allow_peer(self, sandbox_id: str, peer_sandbox_id: str) -> bool:
        boundary = self._boundaries.get(sandbox_id)
        peer_boundary = self._boundaries.get(peer_sandbox_id)
        if not boundary or not peer_boundary:
            return False
        if boundary.comm_policy != CommunicationPolicy.ALLOW_EXPLICIT:
            return False
        if boundary.tenant_id != peer_boundary.tenant_id:
            return False  # cross-tenant peer not allowed
        boundary.allowed_peers.add(peer_sandbox_id)
        return True

    def can_communicate(self, from_sandbox: str, to_sandbox: str) -> dict:
        from_b = self._boundaries.get(from_sandbox)
        to_b = self._boundaries.get(to_sandbox)
        if not from_b or not to_b:
            return {"allowed": False, "reason": "Sandbox not registered"}

        if from_b.comm_policy == CommunicationPolicy.DENY_ALL:
            return {"allowed": False, "reason": "Communication denied by policy"}

        if from_b.comm_policy == CommunicationPolicy.ALLOW_SAME_TENANT:
            if from_b.tenant_id == to_b.tenant_id:
                return {"allowed": True, "reason": "Same tenant"}
            return {"allowed": False, "reason": "Different tenant"}

        if from_b.comm_policy == CommunicationPolicy.ALLOW_EXPLICIT:
            if to_sandbox in from_b.allowed_peers:
                return {"allowed": True, "reason": "Explicitly allowed"}
            return {"allowed": False, "reason": "Not in allowed peers"}

        return {"allowed": False, "reason": "Unknown policy"}

    def can_access_volume(self, sandbox_id: str, volume: str) -> bool:
        boundary = self._boundaries.get(sandbox_id)
        if not boundary:
            return False
        return volume in boundary.shared_volumes

    def share_volume(self, sandbox_id: str, volume: str) -> bool:
        boundary = self._boundaries.get(sandbox_id)
        if not boundary:
            return False
        if boundary.isolation_level == IsolationLevel.FULL:
            return False  # full isolation = no shared volumes
        if volume not in boundary.shared_volumes:
            boundary.shared_volumes.append(volume)
        return True

    def get_tenant_sandboxes(self, tenant_id: str) -> list[str]:
        return [sb_id for sb_id, b in self._boundaries.items()
                if b.tenant_id == tenant_id]

    def get_boundary(self, sandbox_id: str) -> dict | None:
        b = self._boundaries.get(sandbox_id)
        if not b:
            return None
        return {
            "sandbox_id": b.sandbox_id, "tenant_id": b.tenant_id,
            "isolation_level": b.isolation_level.value,
            "namespace": b.namespace,
            "comm_policy": b.comm_policy.value,
            "allowed_peers": sorted(b.allowed_peers),
            "shared_volumes": b.shared_volumes,
        }
