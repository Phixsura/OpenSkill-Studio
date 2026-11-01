from app.services.app_marketplace_app_app_graphql_schema import build_schema_explorer, generate_sdl

def test_explorer():
    types = [
        {"name": "Query", "kind": "OBJECT", "fields": [
            {"name": "app", "type": "App", "args": [{"name": "id", "type": "ID!"}], "description": "Get app by ID"},
            {"name": "apps", "type": "[App!]!", "args": []},
        ]},
        {"name": "App", "kind": "OBJECT", "fields": [
            {"name": "id", "type": "ID!"},
            {"name": "name", "type": "String!"},
        ]},
    ]
    r = build_schema_explorer(types=types)
    assert r["type_count"] == 2
    assert r["query_count"] == 2
    assert r["types"][1]["field_count"] == 2

def test_sdl():
    fields = [{"name": "id", "type": "ID!"}, {"name": "name", "type": "String!", "args": []}]
    sdl = generate_sdl(type_name="App", fields=fields)
    assert "type App {" in sdl
    assert "id: ID!" in sdl
