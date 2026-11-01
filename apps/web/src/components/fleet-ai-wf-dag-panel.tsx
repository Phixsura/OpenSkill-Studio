"use client";
export function FleetAiWfDagPanel({ engines, active, dags, nodes, parallelism }: { engines: number; active: number; dags: number; nodes: number; parallelism: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔀 AI Workflow DAG</h3>
    <div className="text-sm">{active}/{engines} active · {dags.toLocaleString()} DAGs · {nodes.toLocaleString()} nodes · {parallelism}x parallel</div>
  </div>);
}
