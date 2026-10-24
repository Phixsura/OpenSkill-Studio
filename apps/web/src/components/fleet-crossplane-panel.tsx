"use client";
export function FleetCrossplanePanel({ total, ready, synced, notReady, allReady }: { total: number; ready: number; synced: number; notReady: number; allReady: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">☁️ Crossplane</h3>
    <div className="text-sm">{ready}/{total} ready · {synced} synced</div>
    {!allReady && <span className="text-xs text-yellow-600">⚠️ {notReady} not ready</span>}
  </div>);
}
