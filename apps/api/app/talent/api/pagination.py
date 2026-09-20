"""Cursor-based pagination helper for talent API endpoints.

Usage in an endpoint:
    from app.talent.api.pagination import paginate_query

    items, meta = await paginate_query(db, query, cursor=cursor, limit=limit)
    return CursorListResponse(data=[ResponseModel.model_validate(i) for i in items], meta=meta)
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from app.talent.schemas.cursor import CursorMeta


async def paginate_query(
    db: AsyncSession,
    query: Select,
    *,
    cursor: str | None = None,
    limit: int = 50,
    id_column=None,
) -> tuple[list, CursorMeta]:
    """Apply cursor-based pagination.

    NOTE: Uses ULID ordering (time-ordered) which provides natural
    created_at stability. New inserts get higher ULIDs, so pagination
    is stable as long as items are not re-ordered. to a SQLAlchemy select query.

    Args:
        db: Async database session
        query: Base query (should NOT have .limit/.offset applied)
        cursor: ULID cursor — fetch items with id > cursor
        limit: Max items to return
        id_column: The column to use as cursor (defaults to first entity's .id)

    Returns:
        (items, CursorMeta) — items trimmed to limit, meta has next_cursor/has_more
    """
    if id_column is None:
        # Get the first entity's id column from the query
        # This works for select(Model) queries
        entity = query.column_descriptions[0]["entity"]
        id_column = entity.id

    if cursor:
        query = query.where(id_column > cursor)

    # Order by id ascending for deterministic cursor pagination
    query = query.order_by(id_column.asc()).limit(limit + 1)

    result = await db.execute(query)
    items = list(result.scalars().all())

    has_more = len(items) > limit
    if has_more:
        items = items[:limit]

    next_cursor = items[-1].id if has_more and items else None

    return items, CursorMeta(next_cursor=next_cursor, has_more=has_more)
