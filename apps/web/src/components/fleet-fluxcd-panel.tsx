"use client";
export function FleetFluxcdPanel({ total, ready, notReady, suspended, allReady }: { total: number; ready: number; notReady: number; suspended: number; allReady: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔄 FluxCD</h3>
    <div className="text-sm">{ready}/{total} ready · {suspended} suspended</div>
    {!allReady && <span className="text-xs text-yellow-600">⚠️ {notReady} not ready</span>}
  </div>);
}
