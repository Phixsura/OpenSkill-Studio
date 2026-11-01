"""Feature Store — versioned ML features with point-in-time correctness.

Implements:
- Feature groups with schema definitions
- Point-in-time correct lookups (no future leakage)
- Feature versioning with lineage tracking
- Online (low-latency) and offline (batch) serving paths
- Feature statistics and drift detection
"""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import math
from collections import defaultdict


@dataclass
class FeatureSchema:
    name: str
    dtype: str  # int, float, string, bool, list
    description: str = ""
    default: object = None


@dataclass
class FeatureGroup:
    group_id: str
    entity_key: str  # e.g. "user_id", "item_id"
    features: list[FeatureSchema] = field(default_factory=list)
    version: int = 1


@dataclass
class FeatureRecord:
    entity_id: str
    group_id: str
    values: dict[str, object]
    event_time: float  # when the feature was computed
    ingested_at: float = 0.0
    def __post_init__(self):
        if not self.ingested_at: self.ingested_at = time.time()


class FeatureStoreService:
    def __init__(self):
        self._groups: dict[str, FeatureGroup] = {}
        self._online: dict[str, dict[str, FeatureRecord]] = {}  # group -> {entity -> latest}
        self._offline: dict[str, list[FeatureRecord]] = defaultdict(list)  # group -> [records]

    def register_group(self, group_id: str, entity_key: str,
                       features: list[tuple[str, str, str]]) -> FeatureGroup:
        """Register feature group: [(name, dtype, description), ...]"""
        schemas = [FeatureSchema(name=n, dtype=d, description=desc)
                   for n, d, desc in features]
        group = FeatureGroup(group_id=group_id, entity_key=entity_key,
                             features=schemas)
        self._groups[group_id] = group
        self._online[group_id] = {}
        return group

    def ingest(self, group_id: str, entity_id: str, values: dict,
               event_time: float | None = None) -> FeatureRecord:
        """Ingest feature values. Updates both online and offline stores."""
        if group_id not in self._groups:
            raise ValueError(f"Group {group_id} not registered")

        record = FeatureRecord(entity_id=entity_id, group_id=group_id,
                               values=values, event_time=event_time or time.time())

        # Online: keep latest per entity
        current = self._online[group_id].get(entity_id)
        if not current or record.event_time >= current.event_time:
            self._online[group_id][entity_id] = record

        # Offline: append all (for historical lookups)
        self._offline[group_id].append(record)

        return record

    def get_online(self, group_id: str, entity_id: str) -> dict | None:
        """Low-latency lookup of latest feature values."""
        record = self._online.get(group_id, {}).get(entity_id)
        return record.values if record else None

    def get_point_in_time(self, group_id: str, entity_id: str,
                          as_of: float) -> dict | None:
        """Get features as they were at a specific time (no future leakage)."""
        records = self._offline.get(group_id, [])
        # Find latest record for entity before as_of
        candidates = [r for r in records
                      if r.entity_id == entity_id and r.event_time <= as_of]
        if not candidates:
            return None
        latest = max(candidates, key=lambda r: r.event_time)
        return latest.values

    def get_batch(self, group_id: str, entity_ids: list[str],
                  as_of: float | None = None) -> dict[str, dict]:
        """Batch feature retrieval for multiple entities."""
        result = {}
        for eid in entity_ids:
            if as_of:
                vals = self.get_point_in_time(group_id, eid, as_of)
            else:
                vals = self.get_online(group_id, eid)
            if vals:
                result[eid] = vals
        return result

    def compute_stats(self, group_id: str, feature_name: str) -> dict:
        """Compute statistics for a numeric feature across all entities."""
        records = self._online.get(group_id, {})
        values = [r.values.get(feature_name) for r in records.values()
                  if isinstance(r.values.get(feature_name), (int, float))]
        if not values:
            return {"count": 0}
        mean = sum(values) / len(values)
        variance = sum((v - mean) ** 2 for v in values) / len(values)
        return {
            "count": len(values),
            "mean": round(mean, 4),
            "stddev": round(math.sqrt(variance), 4),
            "min": min(values),
            "max": max(values),
        }

    def detect_drift(self, group_id: str, feature_name: str,
                     reference_mean: float, reference_stddev: float,
                     threshold_z: float = 2.0) -> dict:
        """Detect feature drift by comparing current distribution to reference."""
        stats = self.compute_stats(group_id, feature_name)
        if stats["count"] == 0:
            return {"drifted": False, "reason": "no data"}
        z_score = abs(stats["mean"] - reference_mean) / max(0.001, reference_stddev)
        drifted = z_score > threshold_z
        return {
            "drifted": drifted,
            "z_score": round(z_score, 4),
            "current_mean": stats["mean"],
            "reference_mean": reference_mean,
            "threshold": threshold_z,
        }

    def list_groups(self) -> list[dict]:
        return [{"group_id": g.group_id, "entity_key": g.entity_key,
                 "features": len(g.features), "entities": len(self._online.get(g.group_id, {}))}
                for g in self._groups.values()]
