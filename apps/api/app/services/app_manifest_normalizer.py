"""Manifest normalizer — canonicalize manifests for consistent comparison."""

import copy


def normalize_manifest(manifest: dict) -> dict:
    """Normalize a manifest for consistent hashing/comparison."""
    m = copy.deepcopy(manifest)
    # Sort permissions
    if "permissions" in m:
        m["permissions"] = sorted(m["permissions"])
    # Sort event subscriptions
    if "event_subscriptions" in m:
        m["event_subscriptions"] = sorted(m["event_subscriptions"])
    # Sort secrets by key
    if "secrets" in m:
        m["secrets"] = sorted(m["secrets"], key=lambda s: s.get("key", ""))
    # Sort UI extensions by surface
    if "ui_extensions" in m:
        m["ui_extensions"] = sorted(m["ui_extensions"], key=lambda e: e.get("surface", ""))
    # Normalize network hosts
    sandbox = m.get("sandbox", {})
    network = sandbox.get("network", {})
    if "allowed_hosts" in network:
        network["allowed_hosts"] = sorted(h.lower().strip() for h in network["allowed_hosts"])
    return m


def manifests_equal(a: dict, b: dict) -> bool:
    """Check if two manifests are semantically equal (after normalization)."""
    return normalize_manifest(a) == normalize_manifest(b)
