"use client";
export function FleetIstioPanel({ total, synced, outOfSync, versionMismatch, healthy }: { total: number; synced: number; outOfSync: number; versionMismatch: number; healthy: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🕸️ Istio</h3>
    <div className="text-sm">{synced}/{total} synced · {versionMismatch} version mismatches</div>
    {!healthy && <span className="text-xs text-yellow-600">⚠️ {outOfSync} out of sync</span>}
  </div>);
}
