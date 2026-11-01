from app.services.app_marketplace_app_app_app_app_app_app_app_graphql_analyzer import analyze_schema, find_circular_refs

def test_analyze():
    types = [
        {"name": "Query", "kind": "OBJECT", "fields": [{"name": "users"}, {"name": "apps"}]},
        {"name": "Mutation", "kind": "OBJECT", "fields": [{"name": "createApp"}]},
        {"name": "User", "kind": "OBJECT", "fields": [{"name": "id"}, {"name": "email"}, {"name": "name"}]},
        {"name": "App", "kind": "OBJECT", "fields": [{"name": "id"}, {"name": "title"}]},
        {"name": "AppStatus", "kind": "ENUM", "fields": []},
    ]
    r = analyze_schema(types)
    assert r["total_types"] == 5
    assert r["query_count"] == 2
    assert r["mutation_count"] == 1
    assert r["total_fields"] == 8
    assert r["complexity"] == "low"

def test_circular():
    types = [
        {"name": "User", "kind": "OBJECT", "fields": [{"name": "posts", "type_ref": "Post"}]},
        {"name": "Post", "kind": "OBJECT", "fields": [{"name": "author", "type_ref": "User"}]},
    ]
    c = find_circular_refs(types)
    assert len(c) == 1
    assert set(c[0]["types"]) == {"User", "Post"}
