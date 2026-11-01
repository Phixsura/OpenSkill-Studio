"use client";
export function FleetAiIncCmdV2Panel({ commanders, active, incidents, mttr, autoRemediated }: { commanders: number; active: number; incidents: number; mttr: number; autoRemediated: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🚨 AI Incident Commander v2</h3>
    <div className="text-sm">{active}/{commanders} active · {incidents} incidents · MTTR {mttr}m · {autoRemediated} auto-fix</div>
  </div>);
}
