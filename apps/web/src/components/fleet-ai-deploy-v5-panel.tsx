"use client";
export function FleetAiDeployV5Panel({ deployers, active, deploys, rollbacks, leadMin, failPct }: { deployers: number; active: number; deploys: number; rollbacks: number; leadMin: number; failPct: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🚀 AI Deploy v5</h3>
    <div className="text-sm">{active}/{deployers} active · {deploys} deploys · {rollbacks} rollbacks · {leadMin}m lead · {failPct}% fail</div>
  </div>);
}
