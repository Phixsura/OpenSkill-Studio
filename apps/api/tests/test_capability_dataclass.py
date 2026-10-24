"""Capability dataclass tests."""

from dataclasses import fields
from app.services.adapter_sdk import Capability

def test_has_key():
    assert "key" in {f.name for f in fields(Capability)}

def test_has_input_schema():
    assert "input_schema" in {f.name for f in fields(Capability)}

def test_has_output_schema():
    assert "output_schema" in {f.name for f in fields(Capability)}

def test_has_pricing():
    assert "pricing" in {f.name for f in fields(Capability)}

def test_instantiation():
    c = Capability(key="translate", input_schema={"type": "object"}, output_schema={"type": "object"}, pricing={"per_call": 0.01})
    assert c.key == "translate"
