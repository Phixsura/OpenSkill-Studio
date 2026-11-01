"""Consumer Custom Field — store arbitrary metadata per consumer."""
from __future__ import annotations
from dataclasses import dataclass, field
import re
import structlog

log = structlog.get_logger()

FIELD_NAME_RE = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]{0,63}$")

@dataclass
class CustomField:
    name: str
    value: str
    field_type: str = "string"  # "string", "number", "boolean", "json"

@dataclass
class CustomFieldSet:
    consumer_id: str
    fields: dict[str, CustomField] = field(default_factory=dict)

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerCustomField:
    def __init__(self, max_fields: int = 50) -> None:
        self._sets: dict[tuple[str, str], CustomFieldSet] = {}
        self._max = max_fields

    def set_field(self, installation_id: str, consumer_id: str, cf: CustomField) -> CustomField:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not FIELD_NAME_RE.match(cf.name):
            raise ValueError(f"Invalid field name: {cf.name}")
        if cf.field_type not in ("string", "number", "boolean", "json"):
            raise ValueError(f"Invalid field_type: {cf.field_type}")
        if len(cf.value) > 4096:
            raise ValueError("Value too long (max 4096)")
        key = (installation_id, consumer_id)
        if key not in self._sets:
            self._sets[key] = CustomFieldSet(consumer_id=consumer_id)
        fs = self._sets[key]
        if cf.name not in fs.fields and len(fs.fields) >= self._max:
            raise ValueError(f"Max {self._max} fields reached")
        fs.fields[cf.name] = cf
        return cf

    def get_field(self, installation_id: str, consumer_id: str, name: str) -> CustomField | None:
        fs = self._sets.get((installation_id, consumer_id))
        if not fs:
            return None
        return fs.fields.get(name)

    def delete_field(self, installation_id: str, consumer_id: str, name: str) -> None:
        fs = self._sets.get((installation_id, consumer_id))
        if not fs or name not in fs.fields:
            raise ValueError("Field not found")
        del fs.fields[name]

    def list_fields(self, installation_id: str, consumer_id: str) -> list[CustomField]:
        fs = self._sets.get((installation_id, consumer_id))
        if not fs:
            return []
        return sorted(fs.fields.values(), key=lambda f: f.name)
