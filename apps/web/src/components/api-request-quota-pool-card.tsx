"use client";

interface PoolInfo {
  pool_id: string;
  name: string;
  total_capacity: number;
  allocated: number;
  available: number;
  utilization_pct: number;
}

interface APIRequestQuotaPoolCardProps {
  pools: PoolInfo[];
  appName: string;
}

export default function APIRequestQuotaPoolCard({ pools, appName }: APIRequestQuotaPoolCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🏊 Quota Pools</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{pools.length} pools</span>
      </div>

      {pools.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No quota pools</p>
      ) : (
        <div className="space-y-2">
          {pools.map((p) => {
            const barColor = p.utilization_pct >= 90 ? "bg-red-500" : p.utilization_pct >= 70 ? "bg-yellow-500" : "bg-green-500";
            return (
              <div key={p.pool_id}>
                <div className="flex justify-between text-xs">
                  <span className="font-medium text-gray-700 dark:text-gray-300">{p.name}</span>
                  <span className="text-gray-400">{p.allocated}/{p.total_capacity} allocated</span>
                </div>
                <div className="mt-1 h-1.5 w-full rounded-full bg-gray-100 dark:bg-gray-800">
                  <div className={`h-1.5 rounded-full ${barColor}`} style={{ width: `${Math.min(100, p.utilization_pct)}%` }} />
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
