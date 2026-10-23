"""Service map explorer — navigate microservice architecture."""
from __future__ import annotations


def build_service_map(services: list[dict]) -> dict:
    map_data = {"services": {}, "connections": []}
    for s in services:
        map_data["services"][s["name"]] = {
            "type": s.get("type", "service"),
            "team": s.get("team", "unknown"),
            "language": s.get("language", "unknown"),
            "status": s.get("status", "healthy"),
        }
        for dep in s.get("calls", []):
            map_data["connections"].append({"from": s["name"], "to": dep})
    teams = sorted({s.get("team", "") for s in services})
    langs = sorted({s.get("language", "") for s in services})
    return {**map_data, "service_count": len(services),
            "connection_count": len(map_data["connections"]),
            "teams": teams, "languages": langs}


def find_isolated(service_map: dict) -> list[str]:
    connected = set()
    for c in service_map["connections"]:
        connected.add(c["from"])
        connected.add(c["to"])
    return sorted(set(service_map["services"].keys()) - connected)
