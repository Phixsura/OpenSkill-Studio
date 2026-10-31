"""API Documentation Generator — auto-generate docs from endpoint metadata."""
from __future__ import annotations

import structlog
from dataclasses import dataclass, field

logger = structlog.get_logger()


@dataclass
class ParamSpec:
    name: str
    param_type: str  # path, query, header, body
    data_type: str  # string, int, float, bool, object, array
    required: bool = True
    description: str = ""
    example: str = ""


@dataclass
class EndpointDoc:
    endpoint_id: str
    path: str
    method: str
    summary: str
    description: str = ""
    tags: list[str] = field(default_factory=list)
    params: list[ParamSpec] = field(default_factory=list)
    response_example: dict | None = None
    deprecated: bool = False


@dataclass
class DocGenerator:
    """Generate API documentation from endpoint metadata."""

    _endpoints: dict[str, EndpointDoc] = field(default_factory=dict)

    def register(self, doc: EndpointDoc) -> dict:
        if doc.endpoint_id in self._endpoints:
            raise ValueError(f"Endpoint {doc.endpoint_id} already documented")
        if not doc.summary:
            raise ValueError("Summary is required")
        self._endpoints[doc.endpoint_id] = doc
        logger.info("endpoint_documented", endpoint_id=doc.endpoint_id)
        return {"endpoint_id": doc.endpoint_id, "total": len(self._endpoints)}

    def update(self, endpoint_id: str, **kwargs) -> dict:
        doc = self._endpoints.get(endpoint_id)
        if not doc:
            raise ValueError(f"Endpoint {endpoint_id} not found")
        for key, value in kwargs.items():
            if hasattr(doc, key):
                setattr(doc, key, value)
        return {"endpoint_id": endpoint_id, "updated": True}

    def generate_markdown(self, endpoint_id: str) -> str:
        doc = self._endpoints.get(endpoint_id)
        if not doc:
            raise ValueError(f"Endpoint {endpoint_id} not found")
        lines = [f"## {doc.method.upper()} {doc.path}", ""]
        if doc.deprecated:
            lines.append("> **⚠️ Deprecated**\n")
        lines.append(f"**{doc.summary}**\n")
        if doc.description:
            lines.append(f"{doc.description}\n")
        if doc.tags:
            lines.append(f"Tags: {', '.join(doc.tags)}\n")
        if doc.params:
            lines.append("### Parameters\n")
            lines.append("| Name | In | Type | Required | Description |")
            lines.append("|------|-----|------|----------|-------------|")
            for p in doc.params:
                req = "Yes" if p.required else "No"
                lines.append(f"| {p.name} | {p.param_type} | {p.data_type} | {req} | {p.description} |")
            lines.append("")
        if doc.response_example:
            lines.append("### Response Example\n")
            lines.append(f"```json\n{doc.response_example}\n```\n")
        return "\n".join(lines)

    def get_table_of_contents(self) -> list[dict]:
        by_tag: dict[str, list[dict]] = {}
        for doc in self._endpoints.values():
            entry = {"endpoint_id": doc.endpoint_id, "method": doc.method,
                     "path": doc.path, "summary": doc.summary,
                     "deprecated": doc.deprecated}
            tags = doc.tags or ["Uncategorized"]
            for tag in tags:
                by_tag.setdefault(tag, []).append(entry)
        return [{"tag": tag, "endpoints": endpoints}
                for tag, endpoints in sorted(by_tag.items())]

    def search(self, query: str) -> list[dict]:
        query_lower = query.lower()
        results = []
        for doc in self._endpoints.values():
            if (query_lower in doc.summary.lower() or
                query_lower in doc.description.lower() or
                query_lower in doc.path.lower()):
                results.append({"endpoint_id": doc.endpoint_id, "method": doc.method,
                                "path": doc.path, "summary": doc.summary})
        return results

    def get_stats(self) -> dict:
        total = len(self._endpoints)
        deprecated = sum(1 for d in self._endpoints.values() if d.deprecated)
        tags = set()
        for d in self._endpoints.values():
            tags.update(d.tags)
        return {
            "total_endpoints": total,
            "deprecated": deprecated,
            "active": total - deprecated,
            "unique_tags": len(tags),
        }
