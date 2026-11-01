"use client";

interface WorkerPool { name: string; size: number; active: number; idle: number;
  queueDepth: number; processed: number; failureRate: number; healthy: boolean; }
interface WorkerPoolDashboardProps { pools: WorkerPool[]; }

export function WorkerPoolDashboard({ pools }: WorkerPoolDashboardProps) {
  const unhealthy = pools.filter(p => !p.healthy).length;
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">👷 Worker Pools</h3>
        <div className="flex gap-2 text-xs">
          <span className="text-gray-400">{pools.length} pools</span>
          {unhealthy > 0 && <span className="text-red-500">{unhealthy} unhealthy</span>}
        </div>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {pools.map(p => (
          <div key={p.name} className="px-4 py-2.5">
            <div className="flex items-center justify-between mb-1">
              <div className="flex items-center gap-2">
                <span className={`w-2 h-2 rounded-full ${p.healthy ? "bg-green-500" : "bg-red-500"}`} />
                <span className="text-sm font-medium">{p.name}</span>
              </div>
              <span className="text-xs text-gray-400">{p.active}/{p.size} active · {p.queueDepth} queued · {p.processed} done</span>
            </div>
            <div className="w-full h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full">
              <div className="h-full bg-blue-500 rounded-full" style={{ width: `${(p.active / Math.max(p.size, 1)) * 100}%` }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
