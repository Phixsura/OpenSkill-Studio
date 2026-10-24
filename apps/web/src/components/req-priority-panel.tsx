"use client";
interface ReqPriorityPanelProps { byPriority: Record<string, number>; total: number; }
const PRIO_COLOR: Record<string, string> = { critical: "bg-red-500", high: "bg-orange-500", normal: "bg-blue-500", low: "bg-gray-400" };
export function ReqPriorityPanel({ byPriority, total }: ReqPriorityPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🎯 Request Priority</h3>
        <span className="text-xs text-gray-400">{total.toLocaleString()} classified</span>
      </div>
      <div className="p-4 space-y-1.5">
        {Object.entries(byPriority).map(([p, count]) => (
          <div key={p} className="flex items-center gap-2 text-xs">
            <span className={`w-3 h-3 rounded ${PRIO_COLOR[p] ?? "bg-gray-400"}`} />
            <span className="w-16 font-semibold">{p}</span>
            <div className="flex-1 h-2 bg-gray-200 dark:bg-gray-700 rounded-full">
              <div className={`h-full rounded-full ${PRIO_COLOR[p] ?? "bg-gray-400"}`}
                style={{ width: `${count / Math.max(total, 1) * 100}%` }} />
            </div>
            <span className="w-12 text-right text-gray-400">{count}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
