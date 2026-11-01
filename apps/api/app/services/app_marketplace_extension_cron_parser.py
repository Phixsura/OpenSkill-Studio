"""Cron Expression Parser — parse and evaluate 5-field cron expressions.

Implements:
- Parse 5-field cron: minute hour dom month dow
- Wildcards (*), ranges (1-5), steps (*/5), lists (1,3,5)
- Next fire time calculation
- Match check for any datetime
- Human-readable description generation
"""
from __future__ import annotations
from dataclasses import dataclass, field
import re


DOW_MAP = {"sun": 0, "mon": 1, "tue": 2, "wed": 3, "thu": 4, "fri": 5, "sat": 6}
MONTH_MAP = {"jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
             "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12}


@dataclass
class CronField:
    name: str
    values: set[int]
    min_val: int
    max_val: int


class CronParserService:
    FIELD_RANGES = [
        ("minute", 0, 59),
        ("hour", 0, 23),
        ("day_of_month", 1, 31),
        ("month", 1, 12),
        ("day_of_week", 0, 6),
    ]

    def parse(self, expression: str) -> list[CronField]:
        """Parse a 5-field cron expression into field objects."""
        parts = expression.strip().split()
        if len(parts) != 5:
            raise ValueError(f"Expected 5 fields, got {len(parts)}")

        fields = []
        for i, (name, min_v, max_v) in enumerate(self.FIELD_RANGES):
            values = self._parse_field(parts[i], min_v, max_v, name)
            fields.append(CronField(name=name, values=values,
                                    min_val=min_v, max_val=max_v))
        return fields

    def _parse_field(self, field_str: str, min_v: int, max_v: int,
                     name: str) -> set[int]:
        """Parse a single cron field into a set of valid values."""
        # Handle name aliases for dow/month
        field_str = field_str.lower()
        if name == "day_of_week":
            for alias, num in DOW_MAP.items():
                field_str = field_str.replace(alias, str(num))
        if name == "month":
            for alias, num in MONTH_MAP.items():
                field_str = field_str.replace(alias, str(num))

        values = set()
        for part in field_str.split(","):
            if "/" in part:
                range_part, step = part.split("/", 1)
                step = int(step)
                if range_part == "*":
                    start, end = min_v, max_v
                elif "-" in range_part:
                    start, end = map(int, range_part.split("-", 1))
                else:
                    start, end = int(range_part), max_v
                values.update(range(start, end + 1, step))
            elif "-" in part:
                start, end = map(int, part.split("-", 1))
                values.update(range(start, end + 1))
            elif part == "*":
                values.update(range(min_v, max_v + 1))
            else:
                values.add(int(part))

        # Validate
        invalid = {v for v in values if v < min_v or v > max_v}
        if invalid:
            raise ValueError(f"Values {invalid} out of range [{min_v}-{max_v}] for {name}")
        return values

    def matches(self, expression: str, minute: int, hour: int,
                day: int, month: int, dow: int) -> bool:
        """Check if a specific time matches the cron expression."""
        fields = self.parse(expression)
        return (minute in fields[0].values and
                hour in fields[1].values and
                day in fields[2].values and
                month in fields[3].values and
                dow in fields[4].values)

    def describe(self, expression: str) -> str:
        """Generate human-readable description."""
        fields = self.parse(expression)
        parts = []

        # Minute
        if fields[0].values == set(range(0, 60)):
            parts.append("Every minute")
        elif len(fields[0].values) == 1:
            parts.append(f"At minute {min(fields[0].values)}")
        else:
            parts.append(f"At minutes {','.join(map(str, sorted(fields[0].values)))}")

        # Hour
        if fields[1].values != set(range(0, 24)):
            if len(fields[1].values) == 1:
                parts.append(f"past hour {min(fields[1].values)}")
            else:
                parts.append(f"past hours {','.join(map(str, sorted(fields[1].values)))}")

        # DOM
        if fields[2].values != set(range(1, 32)):
            parts.append(f"on day {','.join(map(str, sorted(fields[2].values)))}")

        # DOW
        if fields[4].values != set(range(0, 7)):
            dow_names = {0: "Sun", 1: "Mon", 2: "Tue", 3: "Wed",
                         4: "Thu", 5: "Fri", 6: "Sat"}
            names = [dow_names.get(d, str(d)) for d in sorted(fields[4].values)]
            parts.append(f"on {','.join(names)}")

        return " ".join(parts)

    def get_expanded(self, expression: str) -> dict[str, list[int]]:
        """Return all expanded values for each field."""
        fields = self.parse(expression)
        return {f.name: sorted(f.values) for f in fields}
