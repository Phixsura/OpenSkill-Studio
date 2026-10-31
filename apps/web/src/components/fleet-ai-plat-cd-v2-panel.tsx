"use client";
export function FleetAiPlatCdV2Panel({ pipelines, active, deploys, rollbacks, leadTime }: { pipelines: number; active: number; deploys: number; rollbacks: number; leadTime: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🚀 AI CD v2</h3>
    <div className="text-sm">{active}/{pipelines} active · {deploys} deploys · {rollbacks} rollbacks · {leadTime}m lead time</div>
  </div>);
}
