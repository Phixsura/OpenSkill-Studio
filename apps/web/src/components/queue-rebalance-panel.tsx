"use client";
interface QueueAdj { name: string; current: number; action: string; diff: number; }
interface QueueRebalancePanelProps { queues: QueueAdj[]; totalQueued: number; rebalanceNeeded: boolean; }
const ACTION_COLOR: Record<string, string> = { increase: "text-green-600", decrease: "text-red-500", stable: "text-gray-400" };
export function QueueRebalancePanel({ queues, totalQueued, rebalanceNeeded }: QueueRebalancePanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">⚖️ Queue Rebalancer</h3>
        <span className={`text-xs font-bold ${rebalanceNeeded ? "text-yellow-600" : "text-green-600"}`}>
          {rebalanceNeeded ? "⚠ Rebalance needed" : "✅ Balanced"} · {totalQueued} queued
        </span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {queues.map(q => (
          <div key={q.name} className="flex justify-between px-4 py-1.5 text-xs">
            <span className="font-mono">{q.name} ({q.current})</span>
            <span className={ACTION_COLOR[q.action] ?? ""}>{q.action}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
