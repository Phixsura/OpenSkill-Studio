"use client";
export function FleetDbReplicationV9Panel({ replicas, maxLag }: { replicas: number; maxLag: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🗄️ DB Replication v9</h3>
    <div className="text-sm">{replicas} replicas · {maxLag}ms max lag</div>
  </div>);
}
