"use client";
export function FleetEtcdPanel({ members, healthy, totalKeys, dbSizeMb, quorum }: { members: number; healthy: number; totalKeys: number; dbSizeMb: number; quorum: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🗃️ etcd Health</h3>
    <div className="text-sm">{healthy}/{members} healthy · {totalKeys.toLocaleString()} keys · {dbSizeMb}MB</div>
    <span className={`text-xs ${quorum ? "text-green-600" : "text-red-500"}`}>{quorum ? "✅ Quorum" : "🚨 No quorum!"}</span>
  </div>);
}
