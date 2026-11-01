"""GraphQL schema registry — manage and version GraphQL schemas."""
from __future__ import annotations
import hashlib
import time


def register_schema(name: str, sdl: str, version: str) -> dict:
    schema_hash = hashlib.sha256(sdl.encode()).hexdigest()[:12]
    types = sdl.count("type ") + sdl.count("input ") + sdl.count("enum ")
    queries = sdl.count("Query")
    mutations = sdl.count("Mutation")
    return {"name": name, "version": version, "hash": schema_hash,
            "type_count": types, "has_queries": queries > 0,
            "has_mutations": mutations > 0, "sdl_length": len(sdl),
            "registered_at": time.time()}


def compare_schemas(old: dict, new: dict) -> dict:
    return {"old_version": old["version"], "new_version": new["version"],
            "old_hash": old["hash"], "new_hash": new["hash"],
            "changed": old["hash"] != new["hash"],
            "type_diff": new["type_count"] - old["type_count"],
            "size_diff": new["sdl_length"] - old["sdl_length"]}


def schema_stats(schemas: list[dict]) -> dict:
    latest = schemas[-1] if schemas else None
    return {"total_versions": len(schemas),
            "latest_version": latest["version"] if latest else None,
            "latest_types": latest["type_count"] if latest else 0,
            "total_growth": schemas[-1]["sdl_length"] - schemas[0]["sdl_length"] if len(schemas) >= 2 else 0}
