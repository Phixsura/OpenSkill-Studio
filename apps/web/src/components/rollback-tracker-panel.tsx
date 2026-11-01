"use client";
interface Rollback { service: string; from: string; to: string; reason: string; triggeredBy: string; }
interface RollbackTrackerPanelProps { rollbacks: Rollback[]; total: number; automated: number; }
export function RollbackTrackerPanel({ rollbacks, total, automated }: RollbackTrackerPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">⏪ Rollback Tracker</h3>
        <span className="text-xs text-gray-400">{total} rollbacks · {automated} auto</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {rollbacks.map((r, i) => (
          <div key={i} className="px-4 py-1.5 text-xs">
            <div className="flex justify-between mb-0.5">
              <span className="font-mono">{r.service}: {r.from} → {r.to}</span>
              <span className="text-gray-400">{r.triggeredBy}</span>
            </div>
            <div className="text-red-500">{r.reason}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
