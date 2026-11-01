"""Query Planner — cost-based query optimizer for data queries.

Simplified SQL-like query planning:
- Scan types: full scan, index scan, index-only scan
- Join strategies: nested loop, hash join
- Cost estimation based on table stats
- Plan selection (cheapest wins)
- Explain plan output
"""
from __future__ import annotations
from dataclasses import dataclass, field
import math


@dataclass
class TableStats:
    name: str
    row_count: int
    avg_row_size: int  # bytes
    indexes: list[str] = field(default_factory=list)
    index_cardinality: dict[str, int] = field(default_factory=dict)


@dataclass
class QueryPlan:
    strategy: str
    estimated_cost: float
    estimated_rows: int
    steps: list[str] = field(default_factory=list)


class QueryPlannerService:
    DISK_SEEK_COST = 4.0  # ms
    SEQ_PAGE_COST = 1.0
    RANDOM_PAGE_COST = 4.0
    CPU_TUPLE_COST = 0.01
    CPU_INDEX_COST = 0.005
    PAGE_SIZE = 8192  # bytes

    def __init__(self):
        self._tables: dict[str, TableStats] = {}

    def register_table(self, name: str, row_count: int, avg_row_size: int = 100,
                       indexes: list[str] | None = None,
                       index_cardinality: dict[str, int] | None = None) -> None:
        self._tables[name] = TableStats(
            name=name, row_count=row_count, avg_row_size=avg_row_size,
            indexes=indexes or [], index_cardinality=index_cardinality or {})

    def plan_scan(self, table: str, filter_col: str | None = None,
                  selectivity: float = 1.0) -> QueryPlan:
        """Plan a table scan with optional filter."""
        stats = self._tables.get(table)
        if not stats:
            return QueryPlan("unknown", float('inf'), 0, ["table not registered"])

        estimated_rows = int(stats.row_count * selectivity)
        plans = []

        # Full table scan
        pages = math.ceil(stats.row_count * stats.avg_row_size / self.PAGE_SIZE)
        full_cost = (pages * self.SEQ_PAGE_COST +
                     stats.row_count * self.CPU_TUPLE_COST)
        plans.append(QueryPlan(
            strategy="seq_scan", estimated_cost=round(full_cost, 2),
            estimated_rows=estimated_rows,
            steps=[f"Seq Scan on {table}", f"Filter: {filter_col}" if filter_col else "No filter",
                   f"Rows: ~{estimated_rows}"]))

        # Index scan (if applicable)
        if filter_col and filter_col in stats.indexes:
            cardinality = stats.index_cardinality.get(filter_col, stats.row_count)
            idx_selectivity = min(selectivity, 1.0 / max(1, cardinality) * estimated_rows)
            idx_rows = max(1, int(stats.row_count * idx_selectivity))
            idx_cost = (idx_rows * self.RANDOM_PAGE_COST +
                        idx_rows * self.CPU_INDEX_COST +
                        idx_rows * self.CPU_TUPLE_COST)
            plans.append(QueryPlan(
                strategy="index_scan", estimated_cost=round(idx_cost, 2),
                estimated_rows=idx_rows,
                steps=[f"Index Scan using idx_{filter_col} on {table}",
                       f"Index Cond: {filter_col} = ?",
                       f"Rows: ~{idx_rows}"]))

            # Index-only scan (if we only need indexed columns)
            idx_only_cost = idx_rows * self.CPU_INDEX_COST
            plans.append(QueryPlan(
                strategy="index_only_scan", estimated_cost=round(idx_only_cost, 2),
                estimated_rows=idx_rows,
                steps=[f"Index Only Scan using idx_{filter_col} on {table}",
                       f"Rows: ~{idx_rows}"]))

        return min(plans, key=lambda p: p.estimated_cost)

    def plan_join(self, left: str, right: str, join_col: str) -> QueryPlan:
        """Plan a join between two tables."""
        left_stats = self._tables.get(left)
        right_stats = self._tables.get(right)
        if not left_stats or not right_stats:
            return QueryPlan("unknown", float('inf'), 0, ["table not found"])

        plans = []
        result_rows = min(left_stats.row_count, right_stats.row_count)

        # Nested loop join
        nl_cost = (left_stats.row_count * right_stats.row_count *
                   self.CPU_TUPLE_COST)
        plans.append(QueryPlan(
            strategy="nested_loop", estimated_cost=round(nl_cost, 2),
            estimated_rows=result_rows,
            steps=[f"Nested Loop Join", f"  Scan {left} ({left_stats.row_count} rows)",
                   f"  Scan {right} ({right_stats.row_count} rows)",
                   f"  Join on {join_col}"]))

        # Hash join
        build_cost = right_stats.row_count * self.CPU_TUPLE_COST
        probe_cost = left_stats.row_count * self.CPU_TUPLE_COST
        hash_cost = build_cost + probe_cost
        plans.append(QueryPlan(
            strategy="hash_join", estimated_cost=round(hash_cost, 2),
            estimated_rows=result_rows,
            steps=[f"Hash Join on {join_col}",
                   f"  Build: hash({right}) - {right_stats.row_count} rows",
                   f"  Probe: scan({left}) - {left_stats.row_count} rows"]))

        # Merge join (if both have index on join col)
        if join_col in left_stats.indexes and join_col in right_stats.indexes:
            merge_cost = ((left_stats.row_count + right_stats.row_count) *
                          self.CPU_INDEX_COST)
            plans.append(QueryPlan(
                strategy="merge_join", estimated_cost=round(merge_cost, 2),
                estimated_rows=result_rows,
                steps=[f"Merge Join on {join_col}",
                       f"  Index Scan {left}",
                       f"  Index Scan {right}"]))

        return min(plans, key=lambda p: p.estimated_cost)

    def explain(self, plan: QueryPlan) -> str:
        """Format plan as EXPLAIN output."""
        lines = [f"Strategy: {plan.strategy} (cost={plan.estimated_cost}, rows={plan.estimated_rows})"]
        for step in plan.steps:
            lines.append(f"  {step}")
        return "\n".join(lines)
