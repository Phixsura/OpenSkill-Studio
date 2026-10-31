"""Consumer API Response Formatter — response format normalization."""
from __future__ import annotations

import json
import structlog
from dataclasses import dataclass, field

logger = structlog.get_logger()

FORMATS = ("json", "xml", "csv", "yaml")


@dataclass
class FormatConfig:
    default_format: str = "json"
    wrap_in_envelope: bool = True
    include_meta: bool = True
    pretty_print: bool = False


@dataclass
class ResponseFormatter:
    """Normalize API response format with content negotiation."""

    _config: FormatConfig = field(default_factory=FormatConfig)
    _format_count: dict[str, int] = field(default_factory=dict)

    def configure(self, default_format: str = "json", wrap_in_envelope: bool = True,
                  include_meta: bool = True, pretty_print: bool = False) -> dict:
        if default_format not in FORMATS:
            raise ValueError(f"Invalid format: {default_format}")
        self._config = FormatConfig(default_format, wrap_in_envelope, include_meta, pretty_print)
        return {"default_format": default_format, "envelope": wrap_in_envelope}

    def format(self, data: dict | list, fmt: str | None = None,
               meta: dict | None = None) -> dict:
        output_format = fmt or self._config.default_format
        if output_format not in FORMATS:
            raise ValueError(f"Unsupported format: {output_format}")
        self._format_count[output_format] = self._format_count.get(output_format, 0) + 1

        if self._config.wrap_in_envelope:
            envelope: dict = {"data": data}
            if self._config.include_meta and meta:
                envelope["meta"] = meta
        else:
            envelope = data if isinstance(data, dict) else {"items": data}

        if output_format == "json":
            indent = 2 if self._config.pretty_print else None
            body = json.dumps(envelope, indent=indent, default=str)
            content_type = "application/json"
        elif output_format == "csv":
            if isinstance(data, list) and data and isinstance(data[0], dict):
                headers = list(data[0].keys())
                rows = [",".join(headers)]
                for item in data:
                    rows.append(",".join(str(item.get(h, "")) for h in headers))
                body = "\n".join(rows)
            else:
                body = json.dumps(envelope, default=str)
            content_type = "text/csv"
        elif output_format == "xml":
            def to_xml(obj: dict | list | str, tag: str = "root") -> str:
                if isinstance(obj, dict):
                    inner = "".join(to_xml(v, k) for k, v in obj.items())
                    return f"<{tag}>{inner}</{tag}>"
                elif isinstance(obj, list):
                    inner = "".join(to_xml(item, "item") for item in obj)
                    return f"<{tag}>{inner}</{tag}>"
                return f"<{tag}>{obj}</{tag}>"
            body = to_xml(envelope)
            content_type = "application/xml"
        else:  # yaml-like
            lines = []
            def to_yaml(obj, indent=0):
                prefix = "  " * indent
                if isinstance(obj, dict):
                    for k, v in obj.items():
                        if isinstance(v, (dict, list)):
                            lines.append(f"{prefix}{k}:")
                            to_yaml(v, indent + 1)
                        else:
                            lines.append(f"{prefix}{k}: {v}")
                elif isinstance(obj, list):
                    for item in obj:
                        if isinstance(item, (dict, list)):
                            lines.append(f"{prefix}-")
                            to_yaml(item, indent + 1)
                        else:
                            lines.append(f"{prefix}- {item}")
            to_yaml(envelope)
            body = "\n".join(lines)
            content_type = "application/yaml"

        return {"body": body, "content_type": content_type, "format": output_format,
                "size_bytes": len(body.encode())}

    def negotiate(self, accept_header: str) -> str:
        accept = accept_header.lower()
        if "xml" in accept:
            return "xml"
        if "csv" in accept:
            return "csv"
        if "yaml" in accept:
            return "yaml"
        return "json"

    def get_config(self) -> dict:
        return {
            "default_format": self._config.default_format,
            "wrap_in_envelope": self._config.wrap_in_envelope,
            "include_meta": self._config.include_meta,
            "pretty_print": self._config.pretty_print,
        }

    def get_stats(self) -> dict:
        return {"format_counts": dict(self._format_count),
                "total_formatted": sum(self._format_count.values())}
