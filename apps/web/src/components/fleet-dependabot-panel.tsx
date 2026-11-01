"use client";
export function FleetDependabotPanel({ total, enabled, securityAlerts, autoMerged }: { total: number; enabled: number; securityAlerts: number; autoMerged: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🤖 Dependabot</h3>
    <div className="text-sm">{enabled}/{total} enabled · {autoMerged} auto-merged/30d</div>
    {securityAlerts > 0 && <span className="text-xs text-red-500">🚨 {securityAlerts} security alerts</span>}
  </div>);
}
