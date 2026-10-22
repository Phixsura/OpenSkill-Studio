from app.services.app_marketplace_app_graphql_schema import generate_graphql_type, generate_query_type, build_schema

def test_type():
    t = generate_graphql_type(name="App", fields=[
        {"name": "id", "type": "id", "required": True},
        {"name": "name", "type": "string", "required": True},
        {"name": "installs", "type": "int"},
    ])
    assert "type App {" in t
    assert "id: ID!" in t
    assert "installs: Int" in t

def test_query():
    q = generate_query_type(queries=[
        {"name": "app", "args": [{"name": "id", "type": "ID!"}], "return_type": "App"},
        {"name": "apps", "args": [], "return_type": "[App]"},
    ])
    assert "app(id: ID!): App" in q
    assert "apps: [App]" in q

def test_schema():
    t = generate_graphql_type(name="App", fields=[{"name": "id", "type": "id"}])
    q = generate_query_type(queries=[{"name": "apps", "return_type": "[App]"}])
    s = build_schema(types=[t], queries=q)
    assert "type App" in s
    assert "type Query" in s
