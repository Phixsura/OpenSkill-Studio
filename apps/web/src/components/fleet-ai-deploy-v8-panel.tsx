"use client";
export function FleetAiDeployV8Panel({ deployers, active, deploys, lead, zeroDt }: { deployers: number; active: number; deploys: number; lead: number; zeroDt: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🚀 AI Deploy v8</h3>
    <div className="text-sm">{active}/{deployers} active · {deploys} deploys · {lead}m lead · {zeroDt ? "✅ zero-DT" : "⚠️"}</div>
  </div>);
}
