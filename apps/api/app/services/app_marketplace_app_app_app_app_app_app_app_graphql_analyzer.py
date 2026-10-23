"""GraphQL introspection analyzer — parse schema and report type stats."""
from __future__ import annotations


def analyze_schema(types: list[dict]) -> dict:
    by_kind: dict[str, int] = {}
    fields_total = 0
    queries = []
    mutations = []
    for t in types:
        kind = t.get("kind", "OBJECT")
        name = t.get("name", "")
        if name.startswith("__"):
            continue
        by_kind[kind] = by_kind.get(kind, 0) + 1
        flds = t.get("fields", [])
        fields_total += len(flds)
        if name == "Query":
            queries = [f["name"] for f in flds]
        elif name == "Mutation":
            mutations = [f["name"] for f in flds]
    return {
        "total_types": sum(by_kind.values()),
        "by_kind": by_kind,
        "total_fields": fields_total,
        "queries": queries, "query_count": len(queries),
        "mutations": mutations, "mutation_count": len(mutations),
        "complexity": "high" if fields_total > 100 else "medium" if fields_total > 30 else "low",
    }


def find_circular_refs(types: list[dict]) -> list[dict]:
    type_map: dict[str, set[str]] = {}
    for t in types:
        name = t.get("name", "")
        refs = set()
        for f in t.get("fields", []):
            ref = f.get("type_ref", "")
            if ref and ref != name:
                refs.add(ref)
        type_map[name] = refs
    circulars = []
    for a, refs_a in type_map.items():
        for b in refs_a:
            if b in type_map and a in type_map[b]:
                pair = tuple(sorted([a, b]))
                entry = {"types": list(pair)}
                if entry not in circulars:
                    circulars.append(entry)
    return circulars
