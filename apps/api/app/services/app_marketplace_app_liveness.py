"""Liveness — Kubernetes liveness probe."""
import os
def liveness_check() -> dict:
    return {"alive": True, "pid": os.getpid()}
