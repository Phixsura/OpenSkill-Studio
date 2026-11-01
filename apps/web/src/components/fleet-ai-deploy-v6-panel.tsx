"use client";
export function FleetAiDeployV6Panel({ deployers, active, deploys, rollbacks, lead, zeroDt }: { deployers: number; active: number; deploys: number; rollbacks: number; lead: number; zeroDt: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🚀 AI Deploy v6</h3>
    <div className="text-sm">{active}/{deployers} active · {deploys} deploys · {rollbacks} rollbacks · {lead}m · {zeroDt ? "✅ zero-DT" : "⚠️"}</div>
  </div>);
}
