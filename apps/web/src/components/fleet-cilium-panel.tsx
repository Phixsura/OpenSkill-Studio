"use client";
export function FleetCiliumPanel({ agents, ready, notReady, policyEnforced, healthy }: { agents: number; ready: number; notReady: number; policyEnforced: number; healthy: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🐝 Cilium</h3>
    <div className="text-sm">{ready}/{agents} ready · {policyEnforced} enforcing policy</div>
    {!healthy && <span className="text-xs text-red-500">⚠️ {notReady} not ready</span>}
  </div>);
}
