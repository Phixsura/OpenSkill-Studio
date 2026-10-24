"use client";

interface QueueStats { pending: number; processed: number; maxSize: number; utilizationPct: number; }
interface QueueDashboardProps { stats: QueueStats; }

export function QueueDashboard({ stats }: QueueDashboardProps) {
  const color = stats.utilizationPct > 80 ? "bg-red-500" : stats.utilizationPct > 50 ? "bg-yellow-500" : "bg-green-500";
  return (
    <div className="space-y-3">
      <h3 className="text-sm font-semibold">Task Queue</h3>
      <div className="grid grid-cols-3 gap-3">
        <div className="rounded-lg border p-3 text-center dark:border-gray-700">
          <p className="text-2xl font-bold">{stats.pending}</p>
          <p className="text-xs text-gray-400">Pending</p>
        </div>
        <div className="rounded-lg border p-3 text-center dark:border-gray-700">
          <p className="text-2xl font-bold">{stats.processed}</p>
          <p className="text-xs text-gray-400">Processed</p>
        </div>
        <div className="rounded-lg border p-3 text-center dark:border-gray-700">
          <p className="text-2xl font-bold">{stats.utilizationPct}%</p>
          <p className="text-xs text-gray-400">Utilization</p>
        </div>
      </div>
      <div className="h-2 rounded-full bg-gray-200 dark:bg-gray-700">
        <div className={`h-full rounded-full transition-all ${color}`} style={{ width: `${stats.utilizationPct}%` }} />
      </div>
    </div>
  );
}
