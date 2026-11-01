"use client";
export function FleetThanosPanel({ stores, healthy, compactionOk, allHealthy }: { stores: number; healthy: number; compactionOk: number; allHealthy: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔮 Thanos</h3>
    <div className="text-sm">{healthy}/{stores} healthy · {compactionOk} compaction OK</div>
  </div>);
}
