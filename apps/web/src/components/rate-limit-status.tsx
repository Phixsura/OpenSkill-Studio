"use client";

interface RateLimitStatusProps { policies: { name: string; limit: number; remaining: number; retryAfter: number }[]; }

export function RateLimitStatus({ policies }: RateLimitStatusProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">⏱️ Rate Limits</h3>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {policies.map(p => {
          const pct = Math.round((1 - p.remaining / Math.max(p.limit, 1)) * 100);
          const color = pct > 90 ? "bg-red-500" : pct > 70 ? "bg-yellow-500" : "bg-blue-500";
          return (
            <div key={p.name} className="px-4 py-3">
              <div className="flex items-center justify-between text-sm mb-1">
                <span className="font-medium">{p.name}</span>
                <span className="text-xs text-gray-400">
                  {p.remaining}/{p.limit} remaining
                  {p.retryAfter > 0 && <span className="text-red-500 ml-1">retry in {p.retryAfter}s</span>}
                </span>
              </div>
              <div className="w-full h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full">
                <div className={`h-full rounded-full ${color}`} style={{ width: `${pct}%` }} />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
