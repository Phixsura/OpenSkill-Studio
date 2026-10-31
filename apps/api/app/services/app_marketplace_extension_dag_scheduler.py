"""DAG Scheduler — execute tasks respecting dependency ordering.

Implements:
- Build DAG from task dependencies
- Cycle detection via DFS coloring
- Topological sort (Kahn's algorithm) for execution order
- Parallel execution levels (tasks at same depth run concurrently)
- Critical path calculation
"""
from __future__ import annotations
from dataclasses import dataclass, field
from collections import deque


@dataclass
class DagTask:
    task_id: str
    name: str
    duration_ms: float = 0.0  # estimated duration
    dependencies: list[str] = field(default_factory=list)
    status: str = "pending"  # pending, ready, running, completed, failed
    result: dict = field(default_factory=dict)


class DagSchedulerService:
    def __init__(self):
        self._tasks: dict[str, DagTask] = {}

    def add_task(self, task_id: str, name: str, dependencies: list[str] | None = None,
                 duration_ms: float = 0) -> DagTask:
        task = DagTask(task_id=task_id, name=name,
                       dependencies=dependencies or [], duration_ms=duration_ms)
        self._tasks[task_id] = task
        return task

    def detect_cycle(self) -> list[str] | None:
        """DFS coloring: WHITE=0, GRAY=1, BLACK=2."""
        color = {tid: 0 for tid in self._tasks}
        parent = {tid: "" for tid in self._tasks}

        def dfs(tid: str) -> list[str] | None:
            color[tid] = 1  # GRAY
            for dep in self._tasks[tid].dependencies:
                if dep not in color:
                    continue
                if color[dep] == 1:
                    # Back edge → cycle
                    cycle = [dep, tid]
                    return cycle
                if color[dep] == 0:
                    result = dfs(dep)
                    if result:
                        return result
            color[tid] = 2  # BLACK
            return None

        for tid in self._tasks:
            if color[tid] == 0:
                cycle = dfs(tid)
                if cycle:
                    return cycle
        return None

    def topological_sort(self) -> list[str]:
        """Kahn's algorithm — returns execution order or raises on cycle."""
        in_degree = {tid: 0 for tid in self._tasks}
        adj: dict[str, list[str]] = {tid: [] for tid in self._tasks}

        for tid, task in self._tasks.items():
            for dep in task.dependencies:
                if dep in self._tasks:
                    adj[dep].append(tid)
                    in_degree[tid] += 1

        queue = deque(tid for tid, deg in in_degree.items() if deg == 0)
        order = []

        while queue:
            tid = queue.popleft()
            order.append(tid)
            for neighbor in adj[tid]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(order) != len(self._tasks):
            raise ValueError("Cycle detected — cannot schedule")
        return order

    def get_parallel_levels(self) -> list[list[str]]:
        """Group tasks into levels that can run in parallel."""
        in_degree = {tid: 0 for tid in self._tasks}
        adj: dict[str, list[str]] = {tid: [] for tid in self._tasks}

        for tid, task in self._tasks.items():
            for dep in task.dependencies:
                if dep in self._tasks:
                    adj[dep].append(tid)
                    in_degree[tid] += 1

        levels = []
        current = [tid for tid, deg in in_degree.items() if deg == 0]

        while current:
            levels.append(sorted(current))
            next_level = []
            for tid in current:
                for neighbor in adj[tid]:
                    in_degree[neighbor] -= 1
                    if in_degree[neighbor] == 0:
                        next_level.append(neighbor)
            current = next_level

        return levels

    def critical_path(self) -> tuple[list[str], float]:
        """Find the longest path (by duration) through the DAG."""
        order = self.topological_sort()
        dist: dict[str, float] = {tid: 0.0 for tid in self._tasks}
        prev: dict[str, str] = {tid: "" for tid in self._tasks}

        for tid in order:
            task = self._tasks[tid]
            for dep in task.dependencies:
                if dep in dist:
                    new_dist = dist[dep] + self._tasks[dep].duration_ms
                    if new_dist > dist[tid]:
                        dist[tid] = new_dist
                        prev[tid] = dep

        # Add duration of final task
        for tid in dist:
            dist[tid] += self._tasks[tid].duration_ms

        if not dist:
            return [], 0

        end_task = max(dist, key=lambda t: dist[t])
        total_duration = dist[end_task]

        # Trace back path
        path = []
        current = end_task
        while current:
            path.append(current)
            current = prev[current]
        path.reverse()
        return path, total_duration

    def get_ready_tasks(self) -> list[str]:
        """Tasks whose dependencies are all completed."""
        return [tid for tid, task in self._tasks.items()
                if task.status == "pending"
                and all(self._tasks[d].status == "completed"
                        for d in task.dependencies if d in self._tasks)]
