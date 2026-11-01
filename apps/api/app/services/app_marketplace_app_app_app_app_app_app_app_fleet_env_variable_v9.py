"""Fleet Env Variable v9 — track environment variable management."""
from __future__ import annotations
def fleet_env_variable_v9(vars: list[dict]) -> dict:
    encrypted = [v for v in vars if v.get("encrypted")]
    rotated = [v for v in vars if v.get("rotated_recently")]
    envs = len({v.get("env") for v in vars if v.get("env")})
    return {"total": len(vars), "encrypted": len(encrypted), "rotated_recently": len(rotated),
            "environments": envs, "healthy": len(encrypted) == len(vars)}
