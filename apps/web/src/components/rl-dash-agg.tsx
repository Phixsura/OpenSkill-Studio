"use client";

interface RlKey { key: string; allowed: number; denied: number; total: number; denyRate: number; }
interface RlDashAggProps { keys: RlKey[]; totalDenied: number; totalEvents: number; }

export function RlDashAgg({ keys, totalDenied, totalEvents }: RlDashAggProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🚫 Rate Limits</h3>
        <span className="text-xs text-gray-400">{totalDenied} denied / {totalEvents} total</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {keys.map(k => (
          <div key={k.key} className="flex items-center justify-between px-4 py-1.5 text-xs">
            <span className="font-mono">{k.key}</span>
            <span className={k.denyRate > 50 ? "text-red-500" : "text-gray-400"}>{k.denyRate}% denied</span>
          </div>
        ))}
      </div>
    </div>
  );
}
