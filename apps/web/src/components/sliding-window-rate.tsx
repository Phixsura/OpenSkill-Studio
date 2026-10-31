"use client";

interface SlidingWindowRateProps { keys: { key: string; count: number; limit: number;
  remaining: number; allowed: boolean }[]; }

export function SlidingWindowRate({ keys }: SlidingWindowRateProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🪟 Sliding Window Rates</h3>
        <span className="text-xs text-gray-400">{keys.length} tracked</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {keys.map(k => {
          const pct = Math.round((k.count / Math.max(k.limit, 1)) * 100);
          return (
            <div key={k.key} className="px-4 py-2.5">
              <div className="flex justify-between text-xs mb-0.5">
                <span className="font-mono">{k.key}</span>
                <span className={k.allowed ? "text-green-600" : "text-red-500"}>
                  {k.count}/{k.limit} ({k.remaining} left)
                </span>
              </div>
              <div className="w-full h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full">
                <div className={`h-full rounded-full ${pct > 90 ? "bg-red-500" : pct > 70 ? "bg-yellow-500" : "bg-green-500"}`}
                  style={{ width: `${pct}%` }} />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
