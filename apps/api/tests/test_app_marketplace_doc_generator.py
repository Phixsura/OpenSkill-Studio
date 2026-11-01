from app.services.app_marketplace_doc_generator import (
    DocGenerator, APIEndpoint, DocSection,
)


def test_generate_markdown():
    dg = DocGenerator()
    dg.register_endpoint("ext-1", APIEndpoint(
        "GET", "/api/items", "List all items",
        params=[{"name": "page", "type": "integer", "required": False, "description": "Page number"}],
        example_response={"items": [], "total": 0},
    ))
    dg.register_endpoint("ext-1", APIEndpoint(
        "POST", "/api/items", "Create an item",
        request_body={"name": "string", "value": "number"},
    ))
    md = dg.generate_markdown("ext-1", "Items API")
    assert "# Items API" in md
    assert "GET /api/items" in md
    assert "POST /api/items" in md
    assert "`page`" in md


def test_custom_sections():
    dg = DocGenerator()
    dg.add_section("ext-2", DocSection(
        "Getting Started", "Install the extension first.",
        subsections=[DocSection("Configuration", "Set your API key.")],
    ))
    md = dg.generate_markdown("ext-2", "My Extension")
    assert "## Getting Started" in md
    assert "### Configuration" in md
    assert "Set your API key" in md


def test_openapi_stub():
    dg = DocGenerator()
    dg.register_endpoint("ext-3", APIEndpoint(
        "GET", "/api/users", "List users",
        params=[{"name": "limit", "type": "integer", "required": True}],
        response_schema={"type": "array", "items": {"type": "object"}},
    ))
    spec = dg.generate_openapi_stub("ext-3")
    assert spec["openapi"] == "3.0.0"
    assert "/api/users" in spec["paths"]
    get_op = spec["paths"]["/api/users"]["get"]
    assert get_op["summary"] == "List users"
    assert len(get_op["parameters"]) == 1


def test_empty_extension():
    dg = DocGenerator()
    md = dg.generate_markdown("empty", "Empty Docs")
    assert "# Empty Docs" in md
    assert "API Reference" not in md
