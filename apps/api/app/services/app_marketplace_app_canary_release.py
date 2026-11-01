"""Canary release — gradually shift traffic to new version."""

import secrets


def create_canary_release(*, app_id: str, baseline_version: str,
                            canary_version: str, initial_pct: int = 5) -> dict:
    if initial_pct < 1 or initial_pct > 50:
        return {"error": "Initial percentage must be 1-50%"}
    return {
        "release_id": f"rel_{secrets.token_urlsafe(8)}",
        "app_id": app_id,
        "baseline": {"version": baseline_version, "traffic_pct": 100 - initial_pct},
        "canary": {"version": canary_version, "traffic_pct": initial_pct},
        "status": "active",
        "auto_promote": True,
        "rollback_on_error": True,
    }


def advance_canary(*, release: dict, new_pct: int) -> dict:
    if new_pct > 100 or new_pct < release["canary"]["traffic_pct"]:
        return {"error": "Canary percentage can only increase (up to 100%)"}
    if new_pct == 100:
        return {**release, "canary": {**release["canary"], "traffic_pct": 100},
                "baseline": {**release["baseline"], "traffic_pct": 0},
                "status": "promoted"}
    return {**release, "canary": {**release["canary"], "traffic_pct": new_pct},
            "baseline": {**release["baseline"], "traffic_pct": 100 - new_pct},
            "status": "active"}
