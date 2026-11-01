"""Service dependency chain validator — validate no circular deps and max depth."""
from __future__ import annotations


def validate_chain(dependencies: dict[str, list[str]], max_depth: int = 10) -> dict:
    errors = []
    # Check circular dependencies
    def find_cycle(node: str, visited: set, path: list) -> list | None:
        if node in path:
            return path[path.index(node):] + [node]
        if node in visited:
            return None
        visited.add(node)
        path.append(node)
        for dep in dependencies.get(node, []):
            cycle = find_cycle(dep, visited, path)
            if cycle:
                return cycle
        path.pop()
        return None

    cycles = []
    for node in dependencies:
        cycle = find_cycle(node, set(), [])
        if cycle and cycle not in cycles:
            cycles.append(cycle)

    # Check depth
    def depth(node: str, seen: set | None = None) -> int:
        seen = seen or set()
        if node in seen:
            return 0
        seen.add(node)
        deps = dependencies.get(node, [])
        if not deps:
            return 1
        return 1 + max(depth(d, seen) for d in deps)

    max_found = max((depth(n) for n in dependencies), default=0)
    if max_found > max_depth:
        errors.append({"type": "max_depth_exceeded", "depth": max_found, "limit": max_depth})

    return {"valid": len(cycles) == 0 and len(errors) == 0,
            "cycles": cycles, "max_depth": max_found, "errors": errors,
            "services": len(dependencies)}
