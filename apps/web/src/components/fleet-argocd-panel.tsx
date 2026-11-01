"use client";
export function FleetArgocdPanel({ total, synced, healthy, degraded, allSynced }: { total: number; synced: number; healthy: number; degraded: number; allSynced: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔄 ArgoCD</h3>
    <div className="text-sm">{synced}/{total} synced · {healthy} healthy · {degraded} degraded</div>
    {!allSynced && <span className="text-xs text-yellow-600">⚠️ Out of sync</span>}
  </div>);
}
