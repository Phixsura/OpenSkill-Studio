from app.services.app_marketplace_app_app_app_app_app_app_app_gql_registry import register_schema, compare_schemas, schema_stats

def test_register():
    r = register_schema("api", "type Query { users: [User] } type User { id: ID name: String }", "1.0")
    assert r["type_count"] == 2
    assert r["has_queries"]
    assert len(r["hash"]) == 12

def test_compare():
    s1 = register_schema("api", "type Query { a: Int }", "1.0")
    s2 = register_schema("api", "type Query { a: Int b: String } type Mutation { c: Bool }", "2.0")
    r = compare_schemas(s1, s2)
    assert r["changed"]
    assert r["type_diff"] == 1

def test_stats():
    schemas = [
        register_schema("api", "type A { x: Int }", "1.0"),
        register_schema("api", "type A { x: Int } type B { y: String }", "2.0"),
    ]
    r = schema_stats(schemas)
    assert r["total_versions"] == 2
    assert r["latest_version"] == "2.0"
