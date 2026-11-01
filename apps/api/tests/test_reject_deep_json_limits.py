"""reject_deep_json — exact limit boundary tests."""

import pytest
from app.schemas.base import reject_deep_json

def _nest(depth):
    d = "leaf"
    for _ in range(depth):
        d = {"n": d}
    return d

BOUNDARY_CASES = [
    (0, False),    # flat string
    (1, False),    # one level
    (10, False),
    (50, False),
    (63, False),   # just under default 64
    (65, True),    # just over
    (100, True),
]

@pytest.mark.parametrize("depth,should_raise", BOUNDARY_CASES)
def test_depth_boundary(depth, should_raise):
    val = _nest(depth)
    if should_raise:
        with pytest.raises(ValueError):
            reject_deep_json(val, "test")
    else:
        reject_deep_json(val, "test")  # should not raise

def test_custom_limit():
    val = _nest(5)
    reject_deep_json(val, "test", limit=10)  # ok
    with pytest.raises(ValueError):
        reject_deep_json(_nest(15), "test", limit=10)
