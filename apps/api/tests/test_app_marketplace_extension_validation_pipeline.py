from app.services.app_marketplace_extension_validation_pipeline import (
    ValidationPipelineService, Validator
)


def test_required():
    vp = ValidationPipelineService()
    vp.field("name").required()
    r = vp.validate({"name": ""})
    assert r.valid is False
    assert r.errors[0].rule == "required"


def test_type_check():
    vp = ValidationPipelineService()
    vp.field("age").type_of(int)
    assert vp.validate({"age": 25}).valid is True
    assert vp.validate({"age": "old"}).valid is False


def test_range():
    vp = ValidationPipelineService()
    vp.field("score").min_val(0).max_val(100)
    assert vp.validate({"score": 50}).valid is True
    assert vp.validate({"score": -1}).valid is False
    assert vp.validate({"score": 101}).valid is False


def test_pattern():
    vp = ValidationPipelineService()
    vp.field("email").pattern(r'^[\w.+-]+@[\w-]+\.[\w.]+$')
    assert vp.validate({"email": "user@example.com"}).valid is True
    assert vp.validate({"email": "not-email"}).valid is False


def test_enum():
    vp = ValidationPipelineService()
    vp.field("status").one_of(["active", "inactive", "banned"])
    assert vp.validate({"status": "active"}).valid is True
    assert vp.validate({"status": "deleted"}).valid is False


def test_length():
    vp = ValidationPipelineService()
    vp.field("password").min_length(8).max_length(64)
    assert vp.validate({"password": "short"}).valid is False
    assert vp.validate({"password": "long_enough_password"}).valid is True


def test_accumulate_all_errors():
    vp = ValidationPipelineService()
    vp.field("name").required()
    vp.field("email").required().pattern(r'@')
    vp.field("age").type_of(int).min_val(0)
    r = vp.validate({"name": "", "email": "", "age": "old"})
    assert len(r.errors) >= 3  # multiple errors collected


def test_fail_fast():
    vp = ValidationPipelineService()
    vp.field("a").required()
    vp.field("b").required()
    vp.field("c").required()
    r = vp.validate({"a": "", "b": "", "c": ""}, fail_fast=True)
    assert len(r.errors) == 1  # stopped at first


def test_custom_validator():
    vp = ValidationPipelineService()
    vp.field("password").custom(
        "no_spaces", lambda v: " " not in v,
        "Password must not contain spaces")
    assert vp.validate({"password": "good_pw"}).valid is True
    assert vp.validate({"password": "has spaces"}).valid is False


def test_conditional():
    vp = ValidationPipelineService()
    vp.field("type").required()
    shipping = Validator("shipping_address").required("Shipping address required for physical items")
    vp.when(lambda d: d.get("type") == "physical", shipping)
    # Digital → no shipping needed
    assert vp.validate({"type": "digital"}).valid is True
    # Physical → shipping required
    r = vp.validate({"type": "physical"})
    assert r.valid is False
    assert any("shipping" in e.field for e in r.errors)


def test_optional_field():
    vp = ValidationPipelineService()
    vp.field("bio").max_length(500)  # optional, but if present must be ≤500
    assert vp.validate({}).valid is True  # absent = ok
    assert vp.validate({"bio": "short"}).valid is True
    assert vp.validate({"bio": "x" * 501}).valid is False
