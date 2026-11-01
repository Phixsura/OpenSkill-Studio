"use client";
export function FleetWorkflowEngineV9Panel({ total, running }: { total: number; running: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⚡ Workflow Engine v9</h3>
    <div className="text-sm">{total} workflows · {running} running</div>
  </div>);
}
