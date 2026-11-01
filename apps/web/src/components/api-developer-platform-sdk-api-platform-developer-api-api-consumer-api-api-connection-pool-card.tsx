"use client";

interface PoolInfo { consumer_id: string; max_connections: number; active: number; idle: number; utilization_pct: number; reuse_rate: number; }
interface Props { pools: PoolInfo[]; appName: string; }

const barColor = (pct: number) => pct >= 90 ? "bg-red-500" : pct >= 70 ? "bg-yellow-500" : "bg-green-500";

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConnectionPoolCard({ pools, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔌 Connection Pools</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {pools.length} pools</p>
      </div>
      {pools.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No connection pools</p>
      ) : (
        <div className="space-y-2">
          {pools.map((p) => (
            <div key={p.consumer_id} className="text-[11px]">
              <div className="flex justify-between"><span className="text-gray-700 dark:text-gray-300">{p.consumer_id}</span><span className="text-gray-400">{p.active}/{p.max_connections} · {p.reuse_rate}% reuse</span></div>
              <div className="mt-0.5 h-1 w-full rounded-full bg-gray-100 dark:bg-gray-800"><div className={`h-1 rounded-full ${barColor(p.utilization_pct)}`} style={{ width: `${p.utilization_pct}%` }} /></div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
