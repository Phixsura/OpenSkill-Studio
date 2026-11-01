"""The ONLY ops-plane import surface for product code.

Product services/routers call these functions; they must never import
`app.opsplane.models` / `app.opsplane.services` directly.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass
