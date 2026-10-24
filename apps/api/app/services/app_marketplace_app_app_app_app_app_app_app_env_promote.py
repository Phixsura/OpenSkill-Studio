"""Environment promotion pipeline — promote releases across environments."""
from __future__ import annotations
import time

ENVIRONMENTS = ["development", "staging", "production"]


def create_promotion(version: str, from_env: str, to_env: str) -> dict:
    from_idx = ENVIRONMENTS.index(from_env) if from_env in ENVIRONMENTS else -1
    to_idx = ENVIRONMENTS.index(to_env) if to_env in ENVIRONMENTS else -1
    if from_idx == -1 or to_idx == -1:
        return {"valid": False, "error": "invalid_environment"}
    if to_idx <= from_idx:
        return {"valid": False, "error": "can_only_promote_forward"}
    return {"valid": True, "version": version, "from": from_env, "to": to_env,
            "status": "pending", "created_at": time.time(),
            "requires_approval": to_env == "production"}


def promotion_pipeline(version: str) -> dict:
    pipeline = []
    for i, env in enumerate(ENVIRONMENTS):
        pipeline.append({"environment": env, "order": i,
                          "status": "deployed" if i == 0 else "pending",
                          "requires_approval": env == "production"})
    return {"version": version, "pipeline": pipeline,
            "current_env": ENVIRONMENTS[0], "environments": len(ENVIRONMENTS)}
