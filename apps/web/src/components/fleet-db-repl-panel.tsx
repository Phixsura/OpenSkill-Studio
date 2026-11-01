"use client";
export function FleetDbReplPanel({ replicas, maxLag, avgLag, behind, healthy }: { replicas: number; maxLag: number; avgLag: number; behind: number; healthy: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🗄️ DB Replication</h3>
    <div className="text-sm">{replicas} replicas · max {maxLag}ms · avg {avgLag}ms</div>
    {!healthy && <span className="text-xs text-red-500">⚠️ {behind} replicas behind</span>}
  </div>);
}
