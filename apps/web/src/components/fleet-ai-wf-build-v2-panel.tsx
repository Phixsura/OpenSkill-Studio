"use client";
export function FleetAiWfBuildV2Panel({ builders, active, workflows, nodes, executions }: { builders: number; active: number; workflows: number; nodes: number; executions: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔧 AI Workflow Builder v2</h3>
    <div className="text-sm">{active}/{builders} active · {workflows} workflows · {nodes.toLocaleString()} nodes · {executions.toLocaleString()} exec</div>
  </div>);
}
