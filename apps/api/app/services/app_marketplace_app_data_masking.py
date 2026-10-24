"""Data masking — mask sensitive fields in API responses."""

import re


MASK_PATTERNS = {
    "email": lambda v: v[:2] + "***@" + v.split("@")[-1] if "@" in v else "***",
    "phone": lambda v: v[:3] + "****" + v[-2:] if len(v) >= 7 else "****",
    "credit_card": lambda v: "****-****-****-" + v[-4:] if len(v) >= 4 else "****",
    "ssn": lambda _: "***-**-****",
    "api_key": lambda v: v[:4] + "•" * 16 + v[-4:] if len(v) >= 8 else "••••••••",
    "password": lambda _: "••••••••",
}


def mask_field(*, value: str, field_type: str) -> dict:
    masker = MASK_PATTERNS.get(field_type)
    if not masker:
        return {"masked": value, "type": field_type, "applied": False}
    return {"masked": masker(value), "type": field_type, "applied": True}


def mask_object(*, data: dict, sensitive_fields: dict[str, str]) -> dict:
    masked = {}
    fields_masked = 0
    for key, value in data.items():
        if key in sensitive_fields and isinstance(value, str):
            result = mask_field(value=value, field_type=sensitive_fields[key])
            masked[key] = result["masked"]
            if result["applied"]:
                fields_masked += 1
        else:
            masked[key] = value
    return {"data": masked, "fields_masked": fields_masked, "total_fields": len(data)}
