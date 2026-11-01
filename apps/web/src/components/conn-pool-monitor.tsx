"use client";

interface PoolStatus { name: string; active: number; idle: number; total: number;
  maxSize: number; utilization: number; health: string; waiting: number; }
interface ConnPoolMonitorProps { pools: PoolStatus[]; }

const HEALTH_COLORS: Record<string, string> = {
  healthy: "text-green-600", busy: "text-yellow-600", saturated: "text-red-600",
};

export function ConnPoolMonitor({ pools }: ConnPoolMonitorProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔌 Connection Pools</h3>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {pools.map(p => (
          <div key={p.name} className="px-4 py-3">
            <div className="flex items-center justify-between mb-1.5">
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium">{p.name}</span>
                <span className={`text-xs font-medium ${HEALTH_COLORS[p.health] ?? ""}`}>{p.health}</span>
              </div>
              <span className="text-xs text-gray-400">{p.active}/{p.maxSize} active · {p.idle} idle{p.waiting > 0 ? ` · ${p.waiting} waiting` : ""}</span>
            </div>
            <div className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-full">
              <div className={`h-full rounded-full ${p.utilization > 90 ? "bg-red-500" : p.utilization > 70 ? "bg-yellow-500" : "bg-green-500"}`}
                style={{ width: `${p.utilization}%` }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
