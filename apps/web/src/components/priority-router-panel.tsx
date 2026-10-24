"use client";

interface PriorityRouterPanelProps { depths: Record<string, number>; totalQueued: number; processed: number; }

const PRIO_COLOR: Record<string, string> = {
  critical: "bg-red-500", high: "bg-orange-500", normal: "bg-blue-500", low: "bg-gray-400", background: "bg-gray-300",
};

export function PriorityRouterPanel({ depths, totalQueued, processed }: PriorityRouterPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🎯 Priority Router</h3>
        <span className="text-xs text-gray-400">{totalQueued} queued · {processed.toLocaleString()} processed</span>
      </div>
      <div className="p-4 space-y-2">
        {Object.entries(depths).map(([prio, count]) => (
          <div key={prio} className="flex items-center gap-2 text-xs">
            <span className={`w-3 h-3 rounded ${PRIO_COLOR[prio] ?? "bg-gray-400"}`} />
            <span className="w-20 font-semibold">{prio}</span>
            <div className="flex-1 h-2 bg-gray-200 dark:bg-gray-700 rounded-full">
              <div className={`h-full rounded-full ${PRIO_COLOR[prio] ?? "bg-gray-400"}`}
                style={{ width: `${Math.min(count * 10, 100)}%` }} />
            </div>
            <span className="text-gray-400 w-8 text-right">{count}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
