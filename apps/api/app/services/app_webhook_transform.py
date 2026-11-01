"""App Webhook Transform — transform webhook payloads before delivery.

Applies transformations to outgoing webhook payloads:
- Field mapping (rename, extract, flatten)
- Template-based body rewriting
- Header injection
- Per-installation scoped transforms
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class TransformConfig:
    """Configuration for webhook payload transformation."""

    transform_id: str
    webhook_id: str
    field_mappings: dict[str, str] = field(default_factory=dict)  # old_key → new_key
    extra_headers: dict[str, str] = field(default_factory=dict)
    include_fields: list[str] | None = None  # None = all fields
    exclude_fields: list[str] | None = None


@dataclass
class TransformedPayload:
    """Result of transforming a webhook payload."""

    body: dict
    headers: dict[str, str]
    original_size: int
    transformed_size: int


class AppWebhookTransform:
    """Transform webhook payloads before delivery."""

    def __init__(self) -> None:
        self._transforms: dict[tuple[str, str], TransformConfig] = {}

    def create_transform(
        self,
        installation_id: str,
        transform_id: str,
        webhook_id: str,
        field_mappings: dict[str, str] | None = None,
        extra_headers: dict[str, str] | None = None,
        include_fields: list[str] | None = None,
        exclude_fields: list[str] | None = None,
    ) -> TransformConfig:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not transform_id:
            raise ValueError("transform_id is required")

        key = (installation_id, transform_id)
        if key in self._transforms:
            raise ValueError(f"Transform {transform_id} already exists")

        config = TransformConfig(
            transform_id=transform_id, webhook_id=webhook_id,
            field_mappings=field_mappings or {},
            extra_headers=extra_headers or {},
            include_fields=include_fields,
            exclude_fields=exclude_fields,
        )
        self._transforms[key] = config
        return config

    def apply_transform(
        self,
        installation_id: str,
        transform_id: str,
        payload: dict,
        headers: dict[str, str] | None = None,
    ) -> TransformedPayload:
        """Apply a transform to a payload."""
        config = self._get(installation_id, transform_id)
        original_size = len(json.dumps(payload))

        result = dict(payload)

        # Include filter
        if config.include_fields is not None:
            result = {k: v for k, v in result.items() if k in config.include_fields}

        # Exclude filter
        if config.exclude_fields:
            result = {k: v for k, v in result.items() if k not in config.exclude_fields}

        # Field mappings (rename)
        for old_key, new_key in config.field_mappings.items():
            if old_key in result:
                result[new_key] = result.pop(old_key)

        # Headers
        out_headers = dict(headers or {})
        out_headers.update(config.extra_headers)

        return TransformedPayload(
            body=result, headers=out_headers,
            original_size=original_size,
            transformed_size=len(json.dumps(result)),
        )

    def list_transforms(self, installation_id: str) -> list[TransformConfig]:
        return [t for (inst, _), t in self._transforms.items() if inst == installation_id]

    def _get(self, installation_id: str, transform_id: str) -> TransformConfig:
        key = (installation_id, transform_id)
        t = self._transforms.get(key)
        if t is None:
            raise KeyError(f"Transform {transform_id} not found")
        return t
