"""GraphQL schema — schema introspection and type explorer."""

import html


SCALAR_TYPES = {"String", "Int", "Float", "Boolean", "ID", "DateTime", "JSON"}


def build_schema_explorer(*, types: list[dict]) -> dict:
    items = []
    query_count = mutation_count = 0
    for t in types:
        kind = t.get("kind", "OBJECT")
        fields = []
        for f in t.get("fields", []):
            fields.append({
                "name": f["name"],
                "type": html.escape(f.get("type", "String")),
                "args": f.get("args", []),
                "description": html.escape(f.get("description", "")),
                "deprecated": f.get("deprecated", False),
            })
        name = t["name"]
        if name == "Query":
            query_count = len(fields)
        elif name == "Mutation":
            mutation_count = len(fields)
        items.append({
            "name": name, "kind": kind, "fields": fields,
            "field_count": len(fields),
            "is_scalar": name in SCALAR_TYPES,
            "description": html.escape(t.get("description", "")),
        })
    return {"types": items, "type_count": len(items),
            "query_count": query_count, "mutation_count": mutation_count}


def generate_sdl(*, type_name: str, fields: list[dict]) -> str:
    lines = [f"type {type_name} {{"]
    for f in fields:
        args_str = ""
        if f.get("args"):
            args = ", ".join(f'{a["name"]}: {a["type"]}' for a in f["args"])
            args_str = f"({args})"
        lines.append(f"  {f['name']}{args_str}: {f['type']}")
    lines.append("}")
    return "\n".join(lines)
