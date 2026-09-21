"""Source adapters — strict-schema parsers for external feeds (ADR-016 §4).

Each adapter is a PURE function over already-fetched bytes: it never performs
network I/O, never executes code, and extracts only whitelisted fields via
sanitize_text. Unknown fields are dropped (strict schema extraction, Part Q).
"""

import hashlib
import json
from dataclasses import dataclass, field

from app.ecosystem.security import (
    bounded_json_loads,
    looks_like_prompt_injection,
    sanitize_text,
)


@dataclass
class NormalizedItem:
    """One normalized observation candidate produced by an adapter."""

    event_type: str
    entity_kind: str | None
    external_ref: str | None
    normalized: dict
    confidence: float = 1.0
    provenance_url: str | None = None
    effective_at: str | None = None  # ISO-8601, service parses
    raw_fragment: bytes = b""  # hashed for idempotency

    @property
    def raw_hash(self) -> str:
        basis = self.raw_fragment or json.dumps(
            self.normalized, sort_keys=True, default=str
        ).encode()
        return hashlib.sha256(basis).hexdigest()


@dataclass
class Adapter:
    key: str
    version: str
    parse: callable = field(repr=False, default=None)


def _sanitized_model_entry(entry: dict, provenance: str | None) -> dict:
    """Whitelist-extract one model entry. Injection-shaped text is flagged."""
    out = {
        "name": sanitize_text(entry.get("name"), 200),
        "version": sanitize_text(entry.get("version"), 100),
        "official_id": sanitize_text(entry.get("id") or entry.get("official_id"), 200),
        "description": sanitize_text(entry.get("description"), 2000),
        "license": sanitize_text(entry.get("license"), 100),
        "released_at": sanitize_text(entry.get("released_at"), 40),
        "deprecated_at": sanitize_text(entry.get("deprecated_at"), 40),
        "sunset_at": sanitize_text(entry.get("sunset_at"), 40),
        "api_identifier": sanitize_text(entry.get("api_identifier"), 200),
    }
    # Structured sub-objects pass through only known scalar leaves
    limits = entry.get("limits")
    if isinstance(limits, dict):
        out["limits"] = {
            sanitize_text(k, 60): v
            for k, v in limits.items()
            if isinstance(k, str) and isinstance(v, (int, float, str, bool)) and v == v
        }
    modalities = entry.get("modalities")
    if isinstance(modalities, dict):
        out["modalities"] = {
            "inputs": [sanitize_text(x, 30) for x in modalities.get("inputs", []) if isinstance(x, str)][:10],
            "outputs": [sanitize_text(x, 30) for x in modalities.get("outputs", []) if isinstance(x, str)][:10],
        }
    caps = entry.get("capabilities")
    if isinstance(caps, list):
        out["capabilities"] = [sanitize_text(c, 64) for c in caps if isinstance(c, str)][:20]
    pricing = entry.get("pricing")
    if isinstance(pricing, list):
        clean_prices = []
        for p in pricing[:20]:
            if not isinstance(p, dict):
                continue
            try:
                price_val = float(p.get("price"))
            except (TypeError, ValueError):
                continue
            if price_val != price_val or price_val < 0 or price_val > 1e9:
                continue
            clean_prices.append(
                {
                    "unit": sanitize_text(p.get("unit"), 30),
                    "price": price_val,
                    "currency": sanitize_text(p.get("currency"), 3) or "USD",
                    "region": sanitize_text(p.get("region"), 30),
                }
            )
        out["pricing"] = clean_prices
    # Flag injection-shaped free text — stored as data, never as instructions
    joined = " ".join(v for v in (out.get("name"), out.get("description")) if v)
    out["injection_flag"] = looks_like_prompt_injection(joined)
    out = {k: v for k, v in out.items() if v is not None}
    if provenance:
        out["provenance_url"] = provenance
    return out


def parse_json_catalog(raw: bytes, config: dict) -> list[NormalizedItem]:
    """Official provider model catalog: {"models": [{...}, ...]}."""
    data = bounded_json_loads(raw)
    items: list[NormalizedItem] = []
    models = data.get("models") if isinstance(data, dict) else None
    if not isinstance(models, list):
        return items
    provenance = config.get("provenance_url")
    for entry in models[:500]:
        if not isinstance(entry, dict):
            continue
        clean = _sanitized_model_entry(entry, provenance)
        if not clean.get("name"):
            continue
        lifecycle = sanitize_text(entry.get("lifecycle"), 30)
        if lifecycle == "deprecated" or clean.get("deprecated_at") or clean.get("sunset_at"):
            event_type = "model_deprecated"
        else:
            event_type = "model_released"
        items.append(
            NormalizedItem(
                event_type=event_type,
                entity_kind="model_version" if clean.get("version") else "model",
                external_ref=clean.get("official_id") or clean.get("name"),
                normalized=clean,
                provenance_url=provenance,
                effective_at=clean.get("sunset_at") or clean.get("deprecated_at"),
                raw_fragment=json.dumps(entry, sort_keys=True, default=str).encode(),
            )
        )
    return items


def parse_pricing_json(raw: bytes, config: dict) -> list[NormalizedItem]:
    """Vendor pricing feed: {"prices": [{"model": ..., "unit": ..., "price": ...}]}."""
    data = bounded_json_loads(raw)
    items: list[NormalizedItem] = []
    prices = data.get("prices") if isinstance(data, dict) else None
    if not isinstance(prices, list):
        return items
    provenance = config.get("provenance_url")
    for entry in prices[:1000]:
        if not isinstance(entry, dict):
            continue
        try:
            price_val = float(entry.get("price"))
        except (TypeError, ValueError):
            continue
        if price_val != price_val or price_val < 0 or price_val > 1e9:
            continue
        clean = {
            "model": sanitize_text(entry.get("model"), 200),
            "unit": sanitize_text(entry.get("unit"), 30),
            "price": price_val,
            "currency": sanitize_text(entry.get("currency"), 3) or "USD",
            "region": sanitize_text(entry.get("region"), 30),
            "effective_at": sanitize_text(entry.get("effective_at"), 40),
        }
        clean = {k: v for k, v in clean.items() if v is not None}
        if not clean.get("model") or not clean.get("unit"):
            continue
        items.append(
            NormalizedItem(
                event_type="price_changed",
                entity_kind="model",
                external_ref=clean["model"],
                normalized=clean,
                provenance_url=provenance,
                effective_at=clean.get("effective_at"),
                raw_fragment=json.dumps(entry, sort_keys=True, default=str).encode(),
            )
        )
    return items


def parse_github_releases(raw: bytes, config: dict) -> list[NormalizedItem]:
    """GitHub releases API shape: [{"tag_name": ..., "published_at": ..., ...}]."""
    data = bounded_json_loads(raw)
    items: list[NormalizedItem] = []
    if not isinstance(data, list):
        return items
    repo = sanitize_text(config.get("repo"), 200)
    for entry in data[:100]:
        if not isinstance(entry, dict):
            continue
        tag = sanitize_text(entry.get("tag_name"), 100)
        if not tag:
            continue
        clean = {
            "repo": repo,
            "tag": tag,
            "name": sanitize_text(entry.get("name"), 200) or tag,
            "published_at": sanitize_text(entry.get("published_at"), 40),
            "body_excerpt": sanitize_text(entry.get("body"), 1000),
            "prerelease": bool(entry.get("prerelease", False)),
            "injection_flag": looks_like_prompt_injection(str(entry.get("body", ""))[:5000]),
        }
        items.append(
            NormalizedItem(
                event_type="release_published",
                entity_kind="node_package" if config.get("kind") == "node_package" else "tool",
                external_ref=f"{repo}#{tag}" if repo else tag,
                normalized=clean,
                provenance_url=sanitize_text(entry.get("html_url"), 500),
                raw_fragment=json.dumps(
                    {"tag": tag, "published_at": entry.get("published_at")}, sort_keys=True
                ).encode(),
            )
        )
    return items


def parse_huggingface(raw: bytes, config: dict) -> list[NormalizedItem]:
    """Hugging Face model metadata list: [{"modelId": ..., "tags": [...]}]."""
    data = bounded_json_loads(raw)
    items: list[NormalizedItem] = []
    if not isinstance(data, list):
        return items
    for entry in data[:200]:
        if not isinstance(entry, dict):
            continue
        model_id = sanitize_text(entry.get("modelId") or entry.get("id"), 200)
        if not model_id:
            continue
        clean = {
            "official_id": model_id,
            "name": model_id.split("/")[-1],
            "tags": [sanitize_text(t, 60) for t in entry.get("tags", []) if isinstance(t, str)][:30],
            "pipeline_tag": sanitize_text(entry.get("pipeline_tag"), 60),
            "license": sanitize_text(entry.get("license"), 100),
            "downloads": entry.get("downloads") if isinstance(entry.get("downloads"), int) else None,
        }
        clean = {k: v for k, v in clean.items() if v is not None}
        items.append(
            NormalizedItem(
                event_type="model_released",
                entity_kind="model",
                external_ref=model_id,
                normalized=clean,
                provenance_url=f"https://huggingface.co/{model_id}",
                raw_fragment=json.dumps(entry, sort_keys=True, default=str).encode(),
            )
        )
    return items


def parse_comfyui_repo(raw: bytes, config: dict) -> list[NormalizedItem]:
    """ComfyUI workflow index: {"workflows": [{"name":..., "graph": {...}}]}.

    Parses graphs DECLARATIVELY (node class names only). Never downloads or
    executes custom node code.
    """
    data = bounded_json_loads(raw)
    items: list[NormalizedItem] = []
    workflows = data.get("workflows") if isinstance(data, dict) else None
    if not isinstance(workflows, list):
        return items
    provenance = config.get("provenance_url")
    for entry in workflows[:100]:
        if not isinstance(entry, dict):
            continue
        name = sanitize_text(entry.get("name"), 200)
        graph = entry.get("graph")
        if not name or not isinstance(graph, dict):
            continue
        # Raw class_type strings, NOT NFKC-folded (R86: classification must
        # see the exact identifiers the runtime would see)
        node_types = sorted(
            {
                str(node.get("class_type"))[:100]
                for node in graph.values()
                if isinstance(node, dict) and node.get("class_type")
            }
        )[:100]
        graph_hash = hashlib.sha256(
            json.dumps(graph, sort_keys=True, default=str).encode()
        ).hexdigest()
        clean = {
            "name": name,
            "description": sanitize_text(entry.get("description"), 2000),
            "node_types": node_types,
            "node_count": len(graph),
            "graph_hash": graph_hash,
            "injection_flag": looks_like_prompt_injection(
                (entry.get("description") or "")[:5000]
            ),
        }
        clean = {k: v for k, v in clean.items() if v is not None}
        items.append(
            NormalizedItem(
                event_type="workflow_dependency_changed",
                entity_kind="workflow",
                external_ref=name,
                normalized=clean,
                provenance_url=provenance,
                raw_fragment=graph_hash.encode(),
            )
        )
    return items


def parse_manual(raw: bytes, config: dict) -> list[NormalizedItem]:
    """Manual analyst input — payload is already the normalized observation."""
    data = bounded_json_loads(raw)
    if not isinstance(data, dict):
        return []
    event_type = sanitize_text(data.get("event_type"), 40) or "catalog_snapshot"
    return [
        NormalizedItem(
            event_type=event_type,
            entity_kind=sanitize_text(data.get("entity_kind"), 30),
            external_ref=sanitize_text(data.get("external_ref"), 500),
            normalized=data.get("normalized") if isinstance(data.get("normalized"), dict) else {},
            confidence=0.9,
            provenance_url=sanitize_text(data.get("provenance_url"), 2000),
            raw_fragment=raw,
        )
    ]


ADAPTERS: dict[str, Adapter] = {
    "json_catalog": Adapter("json_catalog", "1.0", parse_json_catalog),
    "pricing_json": Adapter("pricing_json", "1.0", parse_pricing_json),
    "github_releases": Adapter("github_releases", "1.0", parse_github_releases),
    "huggingface": Adapter("huggingface", "1.0", parse_huggingface),
    "comfyui_repo": Adapter("comfyui_repo", "1.0", parse_comfyui_repo),
    "manual": Adapter("manual", "1.0", parse_manual),
}
