"""ConformanceCheck dataclass detailed tests."""

import pytest
from dataclasses import fields
from app.services.conformance import ConformanceCheck

def test_field_names():
    actual = {f.name for f in fields(ConformanceCheck)}
    assert {"name", "status", "message", "details"} == actual

def test_pass_status():
    c = ConformanceCheck(name="test", status="pass", message="ok", details={})
    assert c.status == "pass"

def test_fail_status():
    c = ConformanceCheck(name="test", status="fail", message="bad", details={"reason": "x"})
    assert c.status == "fail"

def test_warn_status():
    c = ConformanceCheck(name="test", status="warn", message="maybe", details={})
    assert c.status == "warn"

def test_details_dict():
    c = ConformanceCheck(name="test", status="pass", message="ok", details={"key": "val"})
    assert c.details == {"key": "val"}

def test_name_preserved():
    c = ConformanceCheck(name="manifest_check", status="pass", message="ok", details={})
    assert c.name == "manifest_check"
