"use client";

interface QueueStats { pending: number; processed: number; hasCritical: boolean;
  byPriority: Record<string, number>; }
interface PriorityQueueViewProps { stats: QueueStats; }

const priorityColors: Record<string, string> = {
  critical: "bg-red-500", high: "bg-orange-500", medium: "bg-yellow-500", low: "bg-green-500",
};

export function PriorityQueueView({ stats }: PriorityQueueViewProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">Priority Queue</h3>
        <div className="flex items-center gap-2">
          {stats.hasCritical && <span className="animate-pulse text-xs text-red-600">🚨 Critical</span>}
          <span className="text-xs text-gray-400">{stats.pending} pending · {stats.processed} processed</span>
        </div>
      </div>
      <div className="grid grid-cols-4 gap-2">
        {Object.entries(stats.byPriority).map(([level, count]) => (
          <div key={level} className="rounded-lg border p-3 text-center dark:border-gray-700">
            <div className={`mx-auto mb-1 h-2 w-2 rounded-full ${priorityColors[level] ?? "bg-gray-400"}`} />
            <p className="text-lg font-bold">{count}</p>
            <p className="text-xs text-gray-400 capitalize">{level}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
