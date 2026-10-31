"use client";

interface PoolInfo {
  pool_id: string;
  max_size: number;
  active: number;
  idle: number;
  waiting: number;
  utilization_pct: number;
  avg_acquire_ms: number;
  saturated: boolean;
}

interface ConnectionPoolCardProps {
  pools: PoolInfo[];
  appName: string;
}

export default function ConnectionPoolCard({ pools, appName }: ConnectionPoolCardProps) {
  const saturatedCount = pools.filter((p) => p.saturated).length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            Connection Pools
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {saturatedCount > 0 ? (
          <span className="rounded-full bg-red-100 px-2 py-0.5 text-xs font-medium text-red-700 dark:bg-red-900/30 dark:text-red-400">
            {saturatedCount} saturated
          </span>
        ) : (
          <span className="rounded-full bg-green-100 px-2 py-0.5 text-xs font-medium text-green-700 dark:bg-green-900/30 dark:text-green-400">
            Healthy
          </span>
        )}
      </div>

      {pools.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No connection pools</p>
      ) : (
        <div className="space-y-2.5">
          {pools.map((p) => {
            const barColor =
              p.utilization_pct >= 90
                ? "bg-red-500"
                : p.utilization_pct >= 70
                  ? "bg-yellow-500"
                  : "bg-green-500";
            return (
              <div
                key={p.pool_id}
                className="rounded-lg border border-gray-100 px-3 py-2 dark:border-gray-800"
              >
                <div className="flex items-center justify-between">
                  <span className="font-mono text-xs text-gray-800 dark:text-gray-200">
                    {p.pool_id}
                  </span>
                  <span className="text-[11px] text-gray-400">
                    {p.avg_acquire_ms.toFixed(0)}ms acquire
                  </span>
                </div>
                <div className="mt-1 flex items-center gap-2">
                  <div className="h-1.5 flex-1 rounded-full bg-gray-200 dark:bg-gray-700">
                    <div
                      className={`h-1.5 rounded-full ${barColor}`}
                      style={{ width: `${Math.min(p.utilization_pct, 100)}%` }}
                    />
                  </div>
                  <span className="text-[11px] text-gray-500">{p.utilization_pct}%</span>
                </div>
                <div className="mt-0.5 flex items-center gap-3 text-[10px] text-gray-400">
                  <span>{p.active} active</span>
                  <span>{p.idle} idle</span>
                  {p.waiting > 0 && <span className="text-red-500">{p.waiting} waiting</span>}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
