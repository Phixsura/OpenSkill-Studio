from app.services.app_marketplace_app_graphql_schema import generate_schema

def test_schema():
    types = [{"name": "App", "fields": [
        {"name": "id", "type": "ID", "required": True},
        {"name": "name", "type": "String", "required": True},
        {"name": "rating", "type": "Float"},
    ]}]
    queries = [{"name": "app", "args": [{"name": "id", "type": "ID!"}], "return_type": "App"}]
    mutations = [{"name": "createApp", "args": [{"name": "name", "type": "String!"}], "return_type": "App"}]
    r = generate_schema(types=types, queries=queries, mutations=mutations)
    assert "type App {" in r["schema"]
    assert "id: ID!" in r["schema"]
    assert "type Query {" in r["schema"]
    assert "type Mutation {" in r["schema"]
    assert r["type_count"] == 1

def test_no_mutations():
    r = generate_schema(types=[], queries=[{"name": "ping", "return_type": "String"}])
    assert "Mutation" not in r["schema"]
    assert r["mutation_count"] == 0
