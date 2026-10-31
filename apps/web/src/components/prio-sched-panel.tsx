"use client";
interface PrioSchedPanelProps { depths: Record<string, number>; totalQueued: number; processed: number; }
const PRIO_BAR: Record<string, string> = { critical: "bg-red-500", high: "bg-orange-500", normal: "bg-blue-500", low: "bg-gray-400", background: "bg-gray-300" };
export function PrioSchedPanel({ depths, totalQueued, processed }: PrioSchedPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🎯 Priority Scheduler</h3>
        <span className="text-xs text-gray-400">{totalQueued} queued · {processed.toLocaleString()} processed</span>
      </div>
      <div className="p-4 space-y-1.5">
        {Object.entries(depths).map(([p, count]) => (
          <div key={p} className="flex items-center gap-2 text-xs">
            <span className="w-20 text-gray-500">{p}</span>
            <div className="flex-1 h-2 bg-gray-200 dark:bg-gray-700 rounded-full">
              <div className={`h-full rounded-full ${PRIO_BAR[p] ?? "bg-gray-400"}`}
                style={{ width: `${Math.min(count * 5, 100)}%` }} />
            </div>
            <span className="w-6 text-right text-gray-400">{count}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
