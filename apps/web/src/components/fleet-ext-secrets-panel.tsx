"use client";
export function FleetExtSecretsPanel({ total, synced, failed, healthy }: { total: number; synced: number; failed: number; healthy: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔑 External Secrets</h3>
    <div className="text-sm">{synced}/{total} synced</div>
    {!healthy && <span className="text-xs text-red-500">⚠️ {failed} sync errors</span>}
  </div>);
}
