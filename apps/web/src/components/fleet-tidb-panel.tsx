"use client";
export function FleetTidbPanel({ clusters, healthy, tikvStores, qps }: { clusters: number; healthy: number; tikvStores: number; qps: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔷 TiDB</h3>
    <div className="text-sm">{healthy}/{clusters} healthy · {tikvStores} TiKV · {qps.toLocaleString()} qps</div>
  </div>);
}
