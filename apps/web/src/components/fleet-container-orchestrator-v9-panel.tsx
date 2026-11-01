"use client";
export function FleetContainerOrchestratorV9Panel({ clusters, cpOk }: { clusters: number; cpOk: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">☸️ Container Orchestrator v9</h3>
    <div className="text-sm">{clusters} clusters · {cpOk} control planes OK</div>
  </div>);
}
