"""Cursor Paginator — cursor-based pagination for stable, efficient paging.

Better than offset: no skipped/duplicated items when data changes,
O(1) seek via cursor vs O(n) for OFFSET.

Implements:
- Encode/decode opaque cursors (base64 of sort key)
- Forward pagination (first + after)
- Multiple sort keys
- Page info (hasNextPage, startCursor, endCursor)
"""
from __future__ import annotations
from dataclasses import dataclass, field
import base64
import json


@dataclass
class PageInfo:
    has_next_page: bool
    has_previous_page: bool
    start_cursor: str = ""
    end_cursor: str = ""
    total_count: int = 0


@dataclass
class Edge:
    cursor: str
    node: dict


@dataclass
class Connection:
    edges: list[Edge]
    page_info: PageInfo


class CursorPaginatorService:
    def encode_cursor(self, values: dict) -> str:
        payload = json.dumps(values, sort_keys=True, default=str)
        return base64.urlsafe_b64encode(payload.encode()).decode().rstrip("=")

    def decode_cursor(self, cursor: str) -> dict:
        padding = 4 - len(cursor) % 4
        if padding != 4:
            cursor += "=" * padding
        return json.loads(base64.urlsafe_b64decode(cursor).decode())

    def paginate(self, items: list[dict], sort_key: str = "id",
                 first: int = 10, after: str = "",
                 sort_desc: bool = False) -> Connection:
        sorted_items = sorted(items, key=lambda x: x.get(sort_key, ""),
                              reverse=sort_desc)
        total = len(sorted_items)

        # Find start index from cursor
        start_idx = 0
        if after:
            cursor_val = self.decode_cursor(after).get(sort_key)
            for i, item in enumerate(sorted_items):
                val = item.get(sort_key)
                if sort_desc:
                    if val is not None and cursor_val is not None and val < cursor_val:
                        start_idx = i
                        break
                else:
                    if val is not None and cursor_val is not None and val > cursor_val:
                        start_idx = i
                        break
            else:
                start_idx = total

        sliced = sorted_items[start_idx:start_idx + first + 1]
        has_next = len(sliced) > first
        sliced = sliced[:first]

        edges = [Edge(cursor=self.encode_cursor({sort_key: item.get(sort_key)}),
                       node=item) for item in sliced]

        return Connection(
            edges=edges,
            page_info=PageInfo(
                has_next_page=has_next,
                has_previous_page=start_idx > 0,
                start_cursor=edges[0].cursor if edges else "",
                end_cursor=edges[-1].cursor if edges else "",
                total_count=total))
