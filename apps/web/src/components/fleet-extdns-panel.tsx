"use client";
export function FleetExtdnsPanel({ total, synced, stale, healthy }: { total: number; synced: number; stale: number; healthy: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🌐 external-dns</h3>
    <div className="text-sm">{synced}/{total} synced</div>
    {!healthy && <span className="text-xs text-yellow-600">⚠️ {stale} stale records</span>}
  </div>);
}
