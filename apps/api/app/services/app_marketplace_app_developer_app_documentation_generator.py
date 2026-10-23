"""Documentation generator — auto-generate API docs from endpoint definitions."""


def generate_endpoint_docs(*, endpoints: list[dict]) -> list[dict]:
    docs = []
    for ep in endpoints:
        doc = {
            "title": ep.get("summary", f"{ep.get('method', 'GET')} {ep.get('path', '/')}"),
            "method": ep.get("method", "GET").upper(),
            "path": ep.get("path", "/"),
            "description": ep.get("description", ""),
            "parameters": ep.get("parameters", []),
            "response_example": ep.get("response_example", {"status": "ok"}),
            "auth_required": ep.get("auth_required", True),
        }
        docs.append(doc)
    return docs


def generate_docs_markdown(*, app_name: str, docs: list[dict]) -> str:
    lines = [f"# {app_name} API Reference\n"]
    for doc in docs:
        lines.append(f"## {doc['method']} `{doc['path']}`\n")
        lines.append(f"{doc['description']}\n" if doc["description"] else "")
        if doc["auth_required"]:
            lines.append("**Authentication required**\n")
        if doc["parameters"]:
            lines.append("### Parameters\n")
            for p in doc["parameters"]:
                lines.append(f"- `{p.get('name')}` ({p.get('type', 'string')}): {p.get('description', '')}")
        lines.append("")
    return "\n".join(lines)


def compute_doc_coverage(*, total_endpoints: int, documented_endpoints: int) -> dict:
    pct = round(documented_endpoints / max(total_endpoints, 1) * 100, 1)
    return {"total": total_endpoints, "documented": documented_endpoints,
            "coverage_pct": pct, "fully_documented": pct == 100}
