"""GraphQL schema — generate GraphQL schema for app APIs."""

import re


def generate_schema(*, types: list[dict], queries: list[dict],
                      mutations: list[dict] | None = None) -> dict:
    lines = []
    for t in types:
        safe_name = re.sub(r"[^A-Za-z0-9_]", "", t["name"])
        lines.append(f"type {safe_name} {{")
        for field in t.get("fields", []):
            fname = re.sub(r"[^A-Za-z0-9_]", "", field["name"])
            ftype = field.get("type", "String")
            nullable = "!" if field.get("required", False) else ""
            lines.append(f"  {fname}: {ftype}{nullable}")
        lines.append("}\n")

    lines.append("type Query {")
    for q in queries:
        qname = re.sub(r"[^A-Za-z0-9_]", "", q["name"])
        args = ", ".join(f'{a["name"]}: {a["type"]}' for a in q.get("args", []))
        arg_str = f"({args})" if args else ""
        lines.append(f"  {qname}{arg_str}: {q['return_type']}")
    lines.append("}\n")

    if mutations:
        lines.append("type Mutation {")
        for m in mutations:
            mname = re.sub(r"[^A-Za-z0-9_]", "", m["name"])
            args = ", ".join(f'{a["name"]}: {a["type"]}' for a in m.get("args", []))
            arg_str = f"({args})" if args else ""
            lines.append(f"  {mname}{arg_str}: {m['return_type']}")
        lines.append("}")

    schema = "\n".join(lines)
    return {"schema": schema, "type_count": len(types),
            "query_count": len(queries), "mutation_count": len(mutations or [])}
