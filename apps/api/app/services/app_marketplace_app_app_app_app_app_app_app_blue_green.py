"""Blue-green deploy controller — manage blue-green deployments."""
from __future__ import annotations


def create_deployment(service: str, blue_version: str, green_version: str) -> dict:
    return {"service": service, "blue": {"version": blue_version, "status": "active", "traffic_pct": 100},
            "green": {"version": green_version, "status": "standby", "traffic_pct": 0},
            "active_slot": "blue"}


def switch_traffic(deployment: dict, to_slot: str) -> dict:
    if to_slot not in ("blue", "green"):
        return {"switched": False, "error": "invalid slot"}
    other = "green" if to_slot == "blue" else "blue"
    deployment[to_slot]["traffic_pct"] = 100
    deployment[to_slot]["status"] = "active"
    deployment[other]["traffic_pct"] = 0
    deployment[other]["status"] = "standby"
    deployment["active_slot"] = to_slot
    return {"switched": True, "active": to_slot,
            "version": deployment[to_slot]["version"]}


def deployment_status(deployment: dict) -> dict:
    active = deployment["active_slot"]
    standby = "green" if active == "blue" else "blue"
    return {"service": deployment["service"],
            "active": {"slot": active, "version": deployment[active]["version"]},
            "standby": {"slot": standby, "version": deployment[standby]["version"]},
            "ready_to_switch": deployment[standby]["status"] == "standby"}
