"use client";

interface PoolInfo { destination: string; max_connections: number; active_connections: number; idle_connections: number; utilization_pct: number; healthy: boolean; total_requests_served: number; }
interface Props { pools: PoolInfo[]; totalActive: number; unhealthyCount: number; appName: string; }

export default function APIDeveloperAPIApiWebhookConnectionPoolCard({ pools, totalActive, unhealthyCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔌 Connection Pools</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {totalActive} active</p>
        </div>
        {unhealthyCount > 0 && <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] text-red-700">{unhealthyCount} unhealthy</span>}
      </div>
      {pools.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No connection pools</p>
      ) : (
        <div className="space-y-2">
          {pools.map((p) => (
            <div key={p.destination}>
              <div className="flex items-center justify-between text-[11px]">
                <span className="text-gray-700 dark:text-gray-300">{new URL(p.destination).hostname}</span>
                <span className={p.healthy ? "text-green-600" : "text-red-500 font-bold"}>{p.utilization_pct}%</span>
              </div>
              <div className="mt-0.5 h-1.5 w-full rounded-full bg-gray-100 dark:bg-gray-800">
                <div className={`h-1.5 rounded-full ${p.utilization_pct >= 90 ? "bg-red-500" : p.utilization_pct >= 70 ? "bg-yellow-500" : "bg-green-500"}`} style={{ width: `${p.utilization_pct}%` }} />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
