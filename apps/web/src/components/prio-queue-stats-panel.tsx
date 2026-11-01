"use client";
interface PrioStats { priority: string; count: number; avgWaitMs: number; }
interface PrioQueueStatsPanelProps { priorities: PrioStats[]; totalQueued: number; status: string; pct: number; }
const STATUS_COLOR: Record<string, string> = { healthy: "text-green-600", warning: "text-yellow-600", critical: "text-red-500" };
export function PrioQueueStatsPanel({ priorities, totalQueued, status, pct }: PrioQueueStatsPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📊 Queue Analytics</h3>
        <span className={`text-xs font-bold ${STATUS_COLOR[status] ?? ""}`}>
          {totalQueued} queued ({pct}%) · {status}
        </span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {priorities.map(p => (
          <div key={p.priority} className="flex justify-between px-4 py-1.5 text-xs">
            <span className="font-semibold">{p.priority}</span>
            <span className="text-gray-400">{p.count} items · avg {p.avgWaitMs}ms wait</span>
          </div>
        ))}
      </div>
    </div>
  );
}
