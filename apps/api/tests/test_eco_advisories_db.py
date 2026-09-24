"""Round-30 tests (ADR-016 §38): security advisory registry."""

import pytest
from sqlalchemy import select
from ulid import ULID

from app.core.database import AsyncSessionLocal
from app.ecosystem.models.catalog import AIModel, ExternalNodePackage, ModelVersion
from app.ecosystem.models.observation import ChangeEvent
from app.ecosystem.services.advisories import AdvisoryService
from app.exceptions import AppError
from tests.test_eco_services_db import _mk_user


@pytest.fixture
async def db():
    from app.core.database import engine

    await engine.dispose(close=False)
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()
    await engine.dispose()


async def test_advisory_registration_emits_security_change_once(db):
    admin = await _mk_user(db, "admin")
    svc = AdvisoryService(db)
    ref = f"CVE-2026-{str(ULID()).lower()[:8]}"
    advisory = await svc.create(
        advisory_ref=ref,
        title="RCE in acme-nodes",
        severity="critical",
        affected_ref="acme-nodes",
        affected_kind="node_package",
        affected_range=">=1.0 <2.4",
        fixed_in="2.4.0",
        created_by=admin.id,
    )
    assert advisory.status == "open"
    change = await db.scalar(
        select(ChangeEvent).where(
            ChangeEvent.field == "security_advisory",
            ChangeEvent.new_value["advisory_ref"].as_string() == ref,
        )
    )
    assert change is not None
    assert change.severity == "security_critical"

    # Duplicate ref rejected, unknown severity rejected
    with pytest.raises(AppError) as exc:
        await svc.create(
            advisory_ref=ref, title="dup", severity="high",
            affected_ref="acme-nodes", created_by=admin.id,
        )
    assert exc.value.code == "ECO_ADVISORY_EXISTS"
    with pytest.raises(AppError):
        await svc.create(
            advisory_ref=f"X-{str(ULID()).lower()[:6]}", title="t",
            severity="apocalyptic", affected_ref="x", created_by=admin.id,
        )

    # Status transition
    advisory = await svc.transition(advisory.id, to_status="mitigated", actor_id=admin.id)
    assert advisory.status == "mitigated"


async def test_affected_entities_respects_range_and_fails_open(db):
    admin = await _mk_user(db, "admin")
    tag = str(ULID()).lower()[:8]
    pkg_name = f"acmepack-{tag}"
    pkg = ExternalNodePackage(canonical_name=pkg_name, slug=f"pkg-{tag}")
    db.add(pkg)
    model = AIModel(canonical_name=f"AcmeModel-{tag}", slug=f"am-{tag}")
    db.add(model)
    await db.flush()
    inside = ModelVersion(
        model_id=model.id, version="1.5.0", canonical_name=f"AcmeModel-{tag} 1.5.0"
    )
    outside = ModelVersion(
        model_id=model.id, version="3.0.0", canonical_name=f"AcmeModel-{tag} 3.0.0"
    )
    weird = ModelVersion(
        model_id=model.id, version="nightly-build", canonical_name=f"AcmeModel-{tag} nightly"
    )
    db.add_all([inside, outside, weird])
    await db.flush()

    svc = AdvisoryService(db)
    advisory = await svc.create(
        advisory_ref=f"GHSA-{tag}",
        title="bad weights",
        severity="high",
        affected_ref=f"AcmeModel-{tag}",
        affected_kind="model_version",
        affected_range=">=1.0 <2.0",
        created_by=admin.id,
    )
    affected = await svc.affected_entities(advisory.id)
    by_id = {a["entity_id"]: a for a in affected}
    assert inside.id in by_id and by_id[inside.id]["range_match"] == "confirmed"
    assert outside.id not in by_id  # provably outside the range
    # Unparseable version FAILS OPEN — unknown never means safe
    assert weird.id in by_id and by_id[weird.id]["range_match"] == "unknown_fail_open"
    # Package with a different name untouched
    assert pkg.id not in by_id

async def test_advisory_notifies_watchers_of_affected_entities(db):
    from app.ecosystem.services.watchlists import WatchlistService

    admin = await _mk_user(db, "admin")
    watcher = await _mk_user(db)
    tag = str(ULID()).lower()[:8]
    model = AIModel(canonical_name=f"WatchedGen-{tag}", slug=f"wg-{tag}")
    db.add(model)
    await db.flush()
    inside = ModelVersion(
        model_id=model.id, version="1.2.0", canonical_name=f"WatchedGen-{tag} 1.2.0"
    )
    db.add(inside)
    await db.flush()
    await WatchlistService(db).quick_watch(
        watcher.id, target_kind="model_version", target_id=inside.id
    )

    await AdvisoryService(db).create(
        advisory_ref=f"CVE-W-{tag}",
        title="watched hit",
        severity="critical",
        affected_ref=f"WatchedGen-{tag}",
        affected_kind="model_version",
        affected_range=">=1.0 <2.0",
        created_by=admin.id,
    )
    # Per-entity change event exists with canonical_entity_id → watch fan-out works
    change = await db.scalar(
        select(ChangeEvent).where(
            ChangeEvent.field == "security_advisory_affects",
            ChangeEvent.canonical_entity_id == inside.id,
        )
    )
    assert change is not None
    assert change.severity == "security_critical"
    # Pull view: the watcher sees it in matching_changes
    rows = await WatchlistService(db).matching_changes(watcher.id)
    assert change.id in [c.id for c in rows]

async def test_advisory_watcher_push_fanout_enqueued(db):
    """Round-108 killer: each per-entity advisory change must ENQUEUE the
    eco.notify_watchers outbox row (push fan-out), not just be visible in the
    pull view."""
    from app.controlplane.models.outbox import OutboxMessage

    admin = await _mk_user(db, "admin")
    tag = str(ULID()).lower()[:8]
    model = AIModel(canonical_name=f"PushGen-{tag}", slug=f"pg-{tag}")
    db.add(model)
    await db.flush()
    version = ModelVersion(
        model_id=model.id, version="1.0.0", canonical_name=f"PushGen-{tag} 1.0.0"
    )
    db.add(version)
    await db.flush()
    await AdvisoryService(db).create(
        advisory_ref=f"CVE-P-{tag}",
        title="push hit",
        severity="high",
        affected_ref=f"PushGen-{tag}",
        affected_kind="model_version",
        created_by=admin.id,
    )
    change = await db.scalar(
        select(ChangeEvent).where(
            ChangeEvent.field == "security_advisory_affects",
            ChangeEvent.canonical_entity_id == version.id,
        )
    )
    assert change is not None
    outbox = await db.scalar(
        select(OutboxMessage).where(
            OutboxMessage.topic == "eco.notify_watchers",
            OutboxMessage.payload["change_event_id"].astext == change.id,
        )
    )
    assert outbox is not None, "watcher push fan-out was not enqueued"


async def test_advisory_name_match_is_exact_not_substring(db):
    """Round-108 killer: an advisory for 'fluxsec-<tag>' must NOT hit an
    unrelated model whose name merely CONTAINS that string — loose matching
    would spray false security notifications."""
    admin = await _mk_user(db, "admin")
    tag = str(ULID()).lower()[:8]
    # The alias contains the ref as a SUBSTRING (passes the SQL prefilter)
    # but neither the name nor any alias matches exactly — python-level
    # matching must reject it.
    bystander = AIModel(
        canonical_name=f"superfluxsec-{tag}",
        slug=f"sf-{tag}",
        aliases=[f"xfluxsec-{tag}y"],
    )
    db.add(bystander)
    await db.flush()
    svc = AdvisoryService(db)
    advisory = await svc.create(
        advisory_ref=f"CVE-X-{tag}",
        title="exact only",
        severity="high",
        affected_ref=f"fluxsec-{tag}",
        affected_kind="model",
        created_by=admin.id,
    )
    hits = await svc.affected_entities(advisory.id)
    assert bystander.id not in [h["entity_id"] for h in hits]
