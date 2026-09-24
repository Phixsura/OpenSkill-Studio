"""Watchlists (ADR-016 Part P)."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ecosystem.models.observation import ChangeEvent
from app.ecosystem.models.replacement import WATCH_TARGET_KINDS, WatchItem, Watchlist
from app.ecosystem.security import sanitize_text
from app.exceptions import AppError


class WatchlistService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self, *, owner_id: str, name: str, org_id: str | None = None
    ) -> Watchlist:
        watchlist = Watchlist(
            owner_id=owner_id, name=sanitize_text(name, 200) or "Watchlist", org_id=org_id
        )
        self.db.add(watchlist)
        await self.db.flush()
        return watchlist

    async def update_settings(
        self,
        watchlist_id: str,
        owner_id: str,
        *,
        min_severity: str | None = None,
        muted_until=None,
        clear_mute: bool = False,
    ) -> Watchlist:
        from app.ecosystem.models.observation import SEVERITY_RANK

        watchlist = await self.get_owned(watchlist_id, owner_id)
        if min_severity is not None:
            if min_severity not in SEVERITY_RANK:
                raise AppError("VALIDATION_ERROR", f"Unknown severity: {min_severity}", 422)
            watchlist.min_severity = min_severity
        if clear_mute:
            watchlist.muted_until = None
        elif muted_until is not None:
            watchlist.muted_until = muted_until
        await self.db.flush()
        return watchlist

    async def get_owned(self, watchlist_id: str, owner_id: str) -> Watchlist:
        watchlist = await self.db.get(Watchlist, watchlist_id)
        # Uniform 404 — never a 403 existence oracle
        if not watchlist or watchlist.owner_id != owner_id:
            raise AppError("NOT_FOUND", "Watchlist not found", 404)
        return watchlist

    async def list_for_owner(self, owner_id: str) -> list[Watchlist]:
        rows = await self.db.scalars(
            select(Watchlist).where(Watchlist.owner_id == owner_id).order_by(Watchlist.created_at)
        )
        return list(rows)

    async def delete(self, watchlist_id: str, owner_id: str) -> None:
        watchlist = await self.get_owned(watchlist_id, owner_id)
        await self.db.delete(watchlist)
        await self.db.flush()

    async def add_item(
        self,
        watchlist_id: str,
        owner_id: str,
        *,
        target_kind: str,
        target_id: str | None = None,
        target_ref: str | None = None,
    ) -> WatchItem:
        await self.get_owned(watchlist_id, owner_id)
        if target_kind not in WATCH_TARGET_KINDS:
            raise AppError("VALIDATION_ERROR", f"Unknown target kind: {target_kind}", 422)
        if not target_id and not target_ref:
            raise AppError("VALIDATION_ERROR", "target_id or target_ref required", 422)
        # Screen BEFORE the uniqueness probe — comparing the raw ref against
        # stored (sanitized) values would let control-char variants of the
        # same ref bypass dedupe and double every notification (R97)
        target_ref = sanitize_text(target_ref, 300)
        # Service-level uniqueness (§3.12)
        existing = await self.db.scalar(
            select(WatchItem).where(
                WatchItem.watchlist_id == watchlist_id,
                WatchItem.target_kind == target_kind,
                WatchItem.target_id == target_id,
                WatchItem.target_ref == target_ref,
            )
        )
        if existing:
            return existing
        item = WatchItem(
            watchlist_id=watchlist_id,
            target_kind=target_kind,
            target_id=target_id,
            target_ref=target_ref,
        )
        self.db.add(item)
        await self.db.flush()
        return item

    async def remove_item(self, watchlist_id: str, item_id: str, owner_id: str) -> None:
        await self.get_owned(watchlist_id, owner_id)
        item = await self.db.get(WatchItem, item_id)
        if not item or item.watchlist_id != watchlist_id:
            raise AppError("NOT_FOUND", "Watch item not found", 404)
        await self.db.delete(item)
        await self.db.flush()

    async def list_items(self, watchlist_id: str, owner_id: str) -> list[WatchItem]:
        await self.get_owned(watchlist_id, owner_id)
        rows = await self.db.scalars(
            select(WatchItem).where(WatchItem.watchlist_id == watchlist_id)
        )
        return list(rows)

    async def quick_watch(
        self, owner_id: str, *, target_kind: str, target_id: str
    ) -> tuple:
        """GitHub watch-button bar: one click watches an entity. Gets or
        creates the user's "Default" watchlist and adds the item idempotently.
        Returns (watchlist, item)."""
        # get-or-create fence: a per-user transaction advisory lock keeps two
        # concurrent first clicks from creating two "Default" lists
        from sqlalchemy import text as sql_text

        await self.db.execute(
            sql_text("SELECT pg_advisory_xact_lock(hashtext(:key))"),
            {"key": f"eco-quick-watch:{owner_id}"},
        )
        default = await self.db.scalar(
            select(Watchlist).where(
                Watchlist.owner_id == owner_id, Watchlist.name == "Default"
            )
        )
        if default is None:
            default = await self.create(owner_id=owner_id, name="Default")
        item = await self.add_item(
            default.id, owner_id, target_kind=target_kind, target_id=target_id
        )
        return default, item

    async def matching_changes(
        self, owner_id: str, *, limit: int = 50
    ) -> list[ChangeEvent]:
        """Recent change events touching any watched entity for this user."""
        from app.ecosystem.models.observation import SEVERITY_RANK

        watchlists = await self.list_for_owner(owner_id)
        if not watchlists:
            return []
        items = await self.db.scalars(
            select(WatchItem).where(
                WatchItem.watchlist_id.in_([w.id for w in watchlists])
            )
        )
        # Per-target severity floor: the LOWEST min_severity of any list
        # watching that target wins (most interested list decides)
        floors = {w.id: SEVERITY_RANK.get(w.min_severity or "info", 0) for w in watchlists}
        target_floor: dict[str, int] = {}
        for item in items:
            if not item.target_id:
                continue
            rank = floors.get(item.watchlist_id, 0)
            current = target_floor.get(item.target_id)
            target_floor[item.target_id] = rank if current is None else min(current, rank)
        if not target_floor:
            return []
        rows = await self.db.scalars(
            select(ChangeEvent)
            .where(ChangeEvent.canonical_entity_id.in_(target_floor))
            .order_by(ChangeEvent.detected_at.desc())
            .limit(limit * 3)
        )
        out = []
        for change in rows:
            if SEVERITY_RANK.get(change.severity, 0) >= target_floor.get(
                change.canonical_entity_id, 0
            ):
                out.append(change)
            if len(out) >= limit:
                break
        return out
