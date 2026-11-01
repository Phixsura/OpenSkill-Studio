"""API Doc Generator — auto-generate OpenAPI documentation for extension APIs.

Parses endpoint definitions into OpenAPI 3.0 spec with path parameters,
request/response schemas, authentication requirements, and example generation.
"""
from __future__ import annotations
import json
from dataclasses import dataclass, field


@dataclass
class EndpointParam:
    name: str
    location: str  # path, query, header
    param_type: str  # string, integer, boolean
    required: bool = True
    description: str = ""
    example: str = ""


@dataclass
class EndpointDef:
    method: str
    path: str
    summary: str
    description: str = ""
    tags: list[str] = field(default_factory=list)
    params: list[EndpointParam] = field(default_factory=list)
    request_body: dict | None = None
    response_schema: dict | None = None
    auth_required: bool = True
    deprecated: bool = False


class ApiDocGeneratorService:
    """Generates OpenAPI 3.0 specs from endpoint definitions."""

    def __init__(self):
        self._endpoints: list[EndpointDef] = []
        self._info: dict = {"title": "Extension API", "version": "1.0.0"}
        self._servers: list[dict] = []

    def set_info(self, title: str, version: str, description: str = "") -> None:
        self._info = {"title": title, "version": version}
        if description:
            self._info["description"] = description

    def add_server(self, url: str, description: str = "") -> None:
        self._servers.append({"url": url, **({"description": description} if description else {})})

    def add_endpoint(self, method: str, path: str, summary: str,
                     description: str = "", tags: list[str] | None = None,
                     params: list[dict] | None = None,
                     request_body: dict | None = None,
                     response_schema: dict | None = None,
                     auth_required: bool = True,
                     deprecated: bool = False) -> EndpointDef:
        parsed_params = [
            EndpointParam(
                name=p["name"], location=p.get("in", "query"),
                param_type=p.get("type", "string"),
                required=p.get("required", True),
                description=p.get("description", ""),
                example=str(p.get("example", "")),
            )
            for p in (params or [])
        ]
        ep = EndpointDef(
            method=method.lower(), path=path, summary=summary,
            description=description, tags=tags or [],
            params=parsed_params, request_body=request_body,
            response_schema=response_schema,
            auth_required=auth_required, deprecated=deprecated,
        )
        self._endpoints.append(ep)
        return ep

    def generate(self) -> dict:
        spec: dict = {
            "openapi": "3.0.3",
            "info": self._info,
            "paths": {},
        }
        if self._servers:
            spec["servers"] = self._servers

        # Security scheme
        spec["components"] = {
            "securitySchemes": {
                "bearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"},
                "apiKey": {"type": "apiKey", "in": "header", "name": "X-API-Key"},
            }
        }

        for ep in self._endpoints:
            if ep.path not in spec["paths"]:
                spec["paths"][ep.path] = {}

            operation: dict = {"summary": ep.summary}
            if ep.description:
                operation["description"] = ep.description
            if ep.tags:
                operation["tags"] = ep.tags
            if ep.deprecated:
                operation["deprecated"] = True
            if ep.auth_required:
                operation["security"] = [{"bearerAuth": []}, {"apiKey": []}]

            if ep.params:
                operation["parameters"] = [
                    {
                        "name": p.name, "in": p.location,
                        "required": p.required,
                        "schema": {"type": p.param_type},
                        **({"description": p.description} if p.description else {}),
                        **({"example": p.example} if p.example else {}),
                    }
                    for p in ep.params
                ]

            if ep.request_body:
                operation["requestBody"] = {
                    "required": True,
                    "content": {"application/json": {"schema": ep.request_body}},
                }

            responses: dict = {"200": {"description": "Success"}}
            if ep.response_schema:
                responses["200"]["content"] = {
                    "application/json": {"schema": ep.response_schema}
                }
            operation["responses"] = responses
            spec["paths"][ep.path][ep.method] = operation

        return spec

    def generate_json(self) -> str:
        return json.dumps(self.generate(), indent=2)

    def get_endpoint_count(self) -> int:
        return len(self._endpoints)

    def get_tags(self) -> list[str]:
        tags: set[str] = set()
        for ep in self._endpoints:
            tags.update(ep.tags)
        return sorted(tags)
