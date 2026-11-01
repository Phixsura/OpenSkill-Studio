"""Service dependency chain analyzer — find longest and critical dep chains."""
from __future__ import annotations


def analyze_chains(deps: dict[str, list[str]]) -> dict:
    chains = {}
    for service in deps:
        chain = _build_chain(service, deps, set())
        chains[service] = {"chain": chain, "depth": len(chain) - 1}
    longest = max(chains.values(), key=lambda c: c["depth"]) if chains else None
    critical = [s for s, c in chains.items() if c["depth"] >= 3]
    return {"chains": chains, "service_count": len(deps),
            "max_depth": longest["depth"] if longest else 0,
            "critical_paths": critical, "critical_count": len(critical)}


def _build_chain(node: str, deps: dict, visited: set) -> list[str]:
    if node in visited or node not in deps:
        return [node]
    visited = visited | {node}
    sub_deps = deps.get(node, [])
    if not sub_deps:
        return [node]
    longest_sub = max((_build_chain(d, deps, visited) for d in sub_deps), key=len, default=[])
    return [node] + longest_sub
