"use client";
export function FleetPostgresPanel({ instances, primary, replicas, maxLag, activeConns, healthy }: { instances: number; primary: number; replicas: number; maxLag: number; activeConns: number; healthy: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🐘 PostgreSQL</h3>
    <div className="text-sm">{primary}P/{replicas}R · lag {maxLag}MB · {activeConns} conns</div>
    {!healthy && <span className="text-xs text-red-500">⚠️ Cluster issue</span>}
  </div>);
}
