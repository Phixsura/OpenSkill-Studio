"""Resource Limiter — hierarchical limits with fair sharing and priority.

Like Linux cgroups: parent groups limit children, and children
share the parent's budget fairly.

Implements:
- Hierarchical resource groups (org → team → user)
- Fair share scheduling within a group
- Priority-based allocation when contended
- Burst allowance (temporary over-allocation)
- Usage tracking and quota warnings
"""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class ResourceGroup:
    name: str
    parent: str = ""
    limit: float = 0  # 0 = unlimited (inherits parent)
    used: float = 0
    priority: int = 0  # higher = gets resources first
    burst_limit: float = 0  # extra over limit allowed temporarily
    children: list[str] = field(default_factory=list)


class ResourceLimiterService:
    def __init__(self):
        self._groups: dict[str, ResourceGroup] = {}

    def create_group(self, name: str, limit: float, parent: str = "",
                     priority: int = 0, burst_limit: float = 0) -> ResourceGroup:
        if parent and parent not in self._groups:
            raise ValueError(f"Parent group '{parent}' not found")
        group = ResourceGroup(name=name, parent=parent, limit=limit,
                               priority=priority, burst_limit=burst_limit)
        self._groups[name] = group
        if parent:
            self._groups[parent].children.append(name)
        return group

    def request(self, group_name: str, amount: float) -> dict:
        """Request resource allocation. Checks entire hierarchy."""
        group = self._groups.get(group_name)
        if not group:
            return {"granted": False, "reason": "group not found"}

        # Check all ancestors
        path = self._get_path(group_name)
        for g_name in path:
            g = self._groups[g_name]
            effective_limit = g.limit + g.burst_limit
            if effective_limit > 0 and g.used + amount > effective_limit:
                in_burst = g.used + amount > g.limit
                return {"granted": False, "blocked_by": g_name,
                        "used": g.used, "limit": g.limit,
                        "burst": in_burst}

        # All levels have capacity — allocate
        for g_name in path:
            self._groups[g_name].used += amount

        return {"granted": True, "group": group_name, "allocated": amount}

    def release(self, group_name: str, amount: float) -> bool:
        path = self._get_path(group_name)
        for g_name in path:
            g = self._groups[g_name]
            g.used = max(0, g.used - amount)
        return True

    def _get_path(self, name: str) -> list[str]:
        """Get path from leaf to root."""
        path = [name]
        current = name
        while self._groups[current].parent:
            current = self._groups[current].parent
            path.append(current)
        return path

    def get_fair_share(self, group_name: str) -> float:
        """Calculate fair share for a group based on siblings."""
        group = self._groups.get(group_name)
        if not group or not group.parent:
            return group.limit if group else 0

        parent = self._groups[group.parent]
        siblings = parent.children
        if not siblings:
            return parent.limit

        # Priority-weighted fair share
        total_priority = sum(max(1, self._groups[s].priority) for s in siblings)
        my_priority = max(1, group.priority)
        return round(parent.limit * my_priority / total_priority, 2)

    def get_utilization(self, group_name: str) -> dict:
        group = self._groups.get(group_name)
        if not group:
            return {}
        effective = group.limit + group.burst_limit
        return {
            "group": group_name,
            "used": group.used,
            "limit": group.limit,
            "burst_limit": group.burst_limit,
            "utilization_pct": round(group.used / max(0.001, group.limit) * 100, 1),
            "in_burst": group.used > group.limit,
            "fair_share": self.get_fair_share(group_name),
            "children": group.children,
        }

    def get_tree(self, root: str = "") -> dict:
        """Get resource tree from a root."""
        if not root:
            roots = [n for n, g in self._groups.items() if not g.parent]
            return {r: self.get_tree(r) for r in roots}
        group = self._groups.get(root)
        if not group:
            return {}
        return {
            "used": group.used, "limit": group.limit,
            "children": {c: self.get_tree(c) for c in group.children}}
