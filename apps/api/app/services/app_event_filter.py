"""Event filter builder — construct and validate event subscription filters."""

VALID_OPERATORS = frozenset({"eq", "neq", "gte", "lte", "contains", "in"})


def build_filter(field: str, operator: str, value) -> dict:
    """Build a filter expression."""
    if operator not in VALID_OPERATORS:
        raise ValueError(f"Invalid operator: {operator}. Must be one of: {', '.join(sorted(VALID_OPERATORS))}")
    if not field:
        raise ValueError("Field is required")
    return {"field": field, "operator": operator, "value": value}


def validate_filter(filter_expr: dict) -> list[str]:
    """Validate a filter expression. Returns list of errors."""
    errors = []
    if not isinstance(filter_expr, dict):
        return ["Filter must be an object"]
    if "field" not in filter_expr:
        errors.append("Filter missing 'field'")
    if "operator" not in filter_expr:
        errors.append("Filter missing 'operator'")
    elif filter_expr["operator"] not in VALID_OPERATORS:
        errors.append(f"Invalid operator: {filter_expr['operator']}")
    if "value" not in filter_expr:
        errors.append("Filter missing 'value'")
    return errors


def combine_filters(*filters: dict) -> list[dict]:
    """Combine multiple filters into a list (AND logic)."""
    return [f for f in filters if f]


def matches(data: dict, filter_expr: dict) -> bool:
    """Evaluate a filter against event data."""
    field_path = filter_expr.get("field", "")
    op = filter_expr.get("operator", "eq")
    expected = filter_expr.get("value")

    value = data
    for part in field_path.split("."):
        if isinstance(value, dict):
            value = value.get(part)
        else:
            return False

    if op == "eq": return value == expected
    if op == "neq": return value != expected
    if op == "gte": return value is not None and value >= expected
    if op == "lte": return value is not None and value <= expected
    if op == "contains": return expected in (value or "")
    if op == "in": return value in (expected or [])
    return True
