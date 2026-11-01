"""Data masking engine — mask sensitive fields in data."""
from __future__ import annotations
import re

MASK_RULES = {
    "email": lambda v: re.sub(r"(?<=.).(?=.*@)", "*", v) if "@" in v else v,
    "phone": lambda v: v[:3] + "****" + v[-2:] if len(v) >= 7 else "****",
    "ssn": lambda v: "***-**-" + v[-4:] if len(v) >= 4 else "****",
    "card": lambda v: "**** **** **** " + v[-4:] if len(v) >= 4 else "****",
    "default": lambda v: v[:2] + "*" * max(len(v) - 4, 2) + v[-2:] if len(v) > 4 else "****",
}


def mask_field(value: str, field_type: str = "default") -> str:
    masker = MASK_RULES.get(field_type, MASK_RULES["default"])
    return masker(value)


def mask_record(record: dict, sensitive_fields: dict[str, str]) -> dict:
    masked = {}
    for k, v in record.items():
        if k in sensitive_fields and isinstance(v, str):
            masked[k] = mask_field(v, sensitive_fields[k])
        else:
            masked[k] = v
    return masked


def mask_batch(records: list[dict], sensitive_fields: dict[str, str]) -> dict:
    masked = [mask_record(r, sensitive_fields) for r in records]
    fields_masked = len(sensitive_fields)
    return {"records": masked, "total": len(masked), "fields_masked": fields_masked}
