"use client";

interface RateLimitGaugeProps { buckets: { key: string; tokens: number; capacity: number; fillPct: number }[]; }

export function RateLimitGauge({ buckets }: RateLimitGaugeProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🪣 Rate Limit Buckets</h3>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {buckets.map(b => {
          const color = b.fillPct > 50 ? "bg-green-500" : b.fillPct > 20 ? "bg-yellow-500" : "bg-red-500";
          return (
            <div key={b.key} className="px-4 py-3">
              <div className="flex items-center justify-between mb-1">
                <span className="text-sm font-mono">{b.key}</span>
                <span className="text-xs text-gray-400">{b.tokens}/{b.capacity} tokens ({b.fillPct}%)</span>
              </div>
              <div className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-full">
                <div className={`h-full rounded-full transition-all ${color}`} style={{ width: `${b.fillPct}%` }} />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
