"""Fleet Container Security v9 — track container runtime security posture."""
from __future__ import annotations
def fleet_container_security_v9(containers: list[dict]) -> dict:
    read_only = [c for c in containers if c.get("read_only_fs")]
    non_root = [c for c in containers if c.get("non_root")]
    drop_caps = [c for c in containers if c.get("capabilities_dropped")]
    return {"containers": len(containers), "read_only_fs": len(read_only),
            "non_root": len(non_root), "caps_dropped": len(drop_caps),
            "healthy": len(non_root) == len(containers)}
