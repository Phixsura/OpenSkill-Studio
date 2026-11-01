from app.services.app_marketplace_extension_graphql_schema import ExtGraphQLSchemaService

def test_build_schema():
    svc = ExtGraphQLSchemaService()
    svc.add_type("ext-1", "User", description="A user")
    svc.add_field("ext-1", "User", "id", "ID!")
    svc.add_field("ext-1", "User", "name", "String!")
    sdl = svc.to_sdl("ext-1")
    assert "type User" in sdl
    assert "id: ID!" in sdl

def test_validate():
    svc = ExtGraphQLSchemaService()
    svc.add_type("ext-1", "Post")
    svc.add_field("ext-1", "Post", "author", "UnknownType")
    errors = svc.validate("ext-1")
    assert any("Unknown type" in e for e in errors)

def test_valid_schema():
    svc = ExtGraphQLSchemaService()
    svc.add_type("ext-1", "Query")
    svc.add_field("ext-1", "Query", "users", "[User]")
    svc.add_type("ext-1", "User")
    svc.add_field("ext-1", "User", "id", "ID!")
    errors = svc.validate("ext-1")
    assert len(errors) == 0
