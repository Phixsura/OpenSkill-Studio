"use client";

interface InstanceStats { instance_id: string; requests: number; avg_ms: number; }
interface RoutingDashboardProps { instances: InstanceStats[]; totalDecisions: number; hotInstance?: { instance_id: string; pct: number } | null; }

export function RoutingDashboard({ instances, totalDecisions, hotInstance }: RoutingDashboardProps) {
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold">Smart Routing</h3>
        <span className="text-xs text-gray-400">{totalDecisions.toLocaleString()} decisions</span>
      </div>
      {hotInstance && (
        <div className="mt-2 rounded bg-yellow-50 px-3 py-1.5 text-xs text-yellow-700 dark:bg-yellow-900/20 dark:text-yellow-300">
          ⚠️ {hotInstance.instance_id} handling {hotInstance.pct}% of traffic
        </div>
      )}
      <ul className="mt-3 space-y-1">
        {instances.map(i => {
          const pct = Math.round((i.requests / Math.max(totalDecisions, 1)) * 100);
          return (
            <li key={i.instance_id} className="flex items-center gap-2 text-sm">
              <span className="w-20 truncate font-mono text-xs">{i.instance_id}</span>
              <div className="flex-1 h-2 rounded-full bg-gray-200 dark:bg-gray-700">
                <div className="h-full rounded-full bg-blue-500" style={{ width: `${pct}%` }} />
              </div>
              <span className="w-16 text-right text-xs text-gray-400">{i.requests} ({pct}%)</span>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
