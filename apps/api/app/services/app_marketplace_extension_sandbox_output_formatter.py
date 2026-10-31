"""Sandbox Output Formatter — format and transform extension output data.

Formats output data into JSON, CSV, Markdown, and HTML table formats
with field selection, sorting, truncation, and sanitization.
"""
from __future__ import annotations
import html
import json
from dataclasses import dataclass


class OutputFormatterService:
    """Formats extension output data into various formats."""

    MAX_OUTPUT_SIZE = 5 * 1024 * 1024  # 5MB

    def to_json(self, data: list[dict], pretty: bool = True,
                fields: list[str] | None = None) -> str:
        filtered = self._select_fields(data, fields)
        indent = 2 if pretty else None
        output = json.dumps(filtered, indent=indent, default=str)
        return self._truncate(output)

    def to_csv(self, data: list[dict], fields: list[str] | None = None,
               delimiter: str = ",") -> str:
        if not data:
            return ""
        filtered = self._select_fields(data, fields)
        headers = list(filtered[0].keys()) if filtered else []
        lines = [delimiter.join(headers)]
        for row in filtered:
            values = [self._escape_csv(str(row.get(h, "")), delimiter) for h in headers]
            lines.append(delimiter.join(values))
        return self._truncate("\n".join(lines))

    def to_markdown_table(self, data: list[dict],
                          fields: list[str] | None = None) -> str:
        if not data:
            return ""
        filtered = self._select_fields(data, fields)
        headers = list(filtered[0].keys()) if filtered else []
        lines = ["| " + " | ".join(headers) + " |"]
        lines.append("| " + " | ".join("---" for _ in headers) + " |")
        for row in filtered:
            values = [str(row.get(h, "")) for h in headers]
            lines.append("| " + " | ".join(values) + " |")
        return self._truncate("\n".join(lines))

    def to_html_table(self, data: list[dict],
                      fields: list[str] | None = None) -> str:
        if not data:
            return "<table></table>"
        filtered = self._select_fields(data, fields)
        headers = list(filtered[0].keys()) if filtered else []
        lines = ["<table>", "<thead><tr>"]
        for h in headers:
            lines.append(f"<th>{html.escape(h)}</th>")
        lines.append("</tr></thead><tbody>")
        for row in filtered:
            lines.append("<tr>")
            for h in headers:
                lines.append(f"<td>{html.escape(str(row.get(h, '')))}</td>")
            lines.append("</tr>")
        lines.append("</tbody></table>")
        return self._truncate("\n".join(lines))

    def sort_data(self, data: list[dict], sort_by: str,
                  descending: bool = False) -> list[dict]:
        return sorted(data, key=lambda r: r.get(sort_by, ""),
                       reverse=descending)

    def _select_fields(self, data: list[dict],
                       fields: list[str] | None) -> list[dict]:
        if not fields:
            return data
        return [{k: row.get(k) for k in fields} for row in data]

    def _escape_csv(self, value: str, delimiter: str) -> str:
        if delimiter in value or '"' in value or "\n" in value:
            return '"' + value.replace('"', '""') + '"'
        return value

    def _truncate(self, output: str) -> str:
        if len(output.encode()) > self.MAX_OUTPUT_SIZE:
            return output[:self.MAX_OUTPUT_SIZE] + "\n... (truncated)"
        return output
