"use client";
export function FleetAiBlueGreenPanel({ deploys, active, switches, rollbackS, zeroDowntime }: { deploys: number; active: number; switches: number; rollbackS: number; zeroDowntime: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔵🟢 AI Blue-Green Deploy</h3>
    <div className="text-sm">{active}/{deploys} active · {switches} switches · rollback {rollbackS}s · {zeroDowntime ? "✅ zero-DT" : "⚠️"}</div>
  </div>);
}
