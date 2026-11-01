"use client";
export function FleetAiCanaryDepPanel({ deploys, active, canaryPct, rollbacks, promotions }: { deploys: number; active: number; canaryPct: number; rollbacks: number; promotions: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🐤 AI Canary Deploy</h3>
    <div className="text-sm">{active}/{deploys} active · {canaryPct}% canary · {promotions} promoted · {rollbacks} rolled back</div>
  </div>);
}
