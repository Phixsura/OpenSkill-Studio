"""Consumer API Response Transformer — transform API responses per consumer preferences."""
from __future__ import annotations
from dataclasses import dataclass, field
import json
import structlog

log = structlog.get_logger()

@dataclass
class TransformConfig:
    consumer_id: str
    rename_fields: dict[str, str] = field(default_factory=dict)  # {"old_name": "new_name"}
    exclude_fields: set[str] = field(default_factory=set)
    include_only: set[str] | None = None  # if set, only these fields
    wrap_in_envelope: bool = True  # wrap in {"data": ...}
    format: str = "json"  # "json", "xml_like"

@dataclass
class TransformResult:
    original_size: int
    transformed_size: int
    fields_renamed: int
    fields_excluded: int

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiResponseTransformer:
    def __init__(self) -> None:
        self._configs: dict[tuple[str, str], TransformConfig] = {}

    def set_config(self, installation_id: str, config: TransformConfig) -> TransformConfig:
        if not installation_id:
            raise ValueError("installation_id is required")
        self._configs[(installation_id, config.consumer_id)] = config
        return config

    def transform(self, installation_id: str, consumer_id: str, response: dict) -> tuple[dict, TransformResult]:
        config = self._configs.get((installation_id, consumer_id))
        if not config:
            return response, TransformResult(original_size=len(json.dumps(response)), transformed_size=len(json.dumps(response)), fields_renamed=0, fields_excluded=0)
        original_size = len(json.dumps(response))
        result = dict(response)
        renamed = 0
        excluded = 0
        # Include only
        if config.include_only is not None:
            result = {k: v for k, v in result.items() if k in config.include_only}
            excluded = len(response) - len(result)
        else:
            # Exclude fields
            for f in config.exclude_fields:
                if f in result:
                    del result[f]
                    excluded += 1
        # Rename fields
        for old, new in config.rename_fields.items():
            if old in result:
                result[new] = result.pop(old)
                renamed += 1
        # Wrap
        if config.wrap_in_envelope:
            result = {"data": result}
        transformed_size = len(json.dumps(result))
        return result, TransformResult(original_size=original_size, transformed_size=transformed_size, fields_renamed=renamed, fields_excluded=excluded)

    def get_config(self, installation_id: str, consumer_id: str) -> TransformConfig | None:
        return self._configs.get((installation_id, consumer_id))
