"use client";
export function FleetPipelineOrchestratorV9Panel({ total, success }: { total: number; success: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔧 Pipeline Orchestrator v9</h3>
    <div className="text-sm">{total} pipelines · {success} succeeded</div>
  </div>);
}
