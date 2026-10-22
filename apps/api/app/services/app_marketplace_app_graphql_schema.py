"""GraphQL schema — generate GraphQL type definitions for app data."""


def generate_graphql_type(*, name: str, fields: list[dict]) -> str:
    lines = [f"type {name} {{"]
    for f in fields:
        nullable = "" if f.get("required") else ""
        gql_type = {"string": "String", "int": "Int", "float": "Float", "bool": "Boolean",
                     "id": "ID"}.get(f.get("type", "string"), "String")
        required_mark = "!" if f.get("required") else ""
        lines.append(f"  {f['name']}: {gql_type}{required_mark}")
    lines.append("}")
    return "\n".join(lines)


def generate_query_type(*, queries: list[dict]) -> str:
    lines = ["type Query {"]
    for q in queries:
        args = ", ".join(f"{a['name']}: {a.get('type', 'String')}" for a in q.get("args", []))
        args_str = f"({args})" if args else ""
        lines.append(f"  {q['name']}{args_str}: {q['return_type']}")
    lines.append("}")
    return "\n".join(lines)


def build_schema(*, types: list[str], queries: str) -> str:
    return "\n\n".join(types + [queries])
