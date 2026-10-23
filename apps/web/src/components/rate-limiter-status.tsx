"use client";

interface RateLimiterStatusProps { endpoints: { path: string; limit: number; remaining: number; resetSec: number }[]; }

export function RateLimiterStatus({ endpoints }: RateLimiterStatusProps) {
  return (
    <div className="space-y-3">
      <h2 className="text-lg font-semibold">Rate Limiter</h2>
      {endpoints.map(ep => {
        const pct = Math.round(((ep.limit - ep.remaining) / Math.max(ep.limit, 1)) * 100);
        const color = pct > 90 ? "bg-red-500" : pct > 70 ? "bg-yellow-500" : "bg-green-500";
        return (
          <div key={ep.path} className="rounded border px-3 py-2 dark:border-gray-700">
            <div className="flex justify-between text-sm">
              <span className="font-mono">{ep.path}</span>
              <span className="text-gray-400">{ep.remaining}/{ep.limit}</span>
            </div>
            <div className="mt-1 h-1.5 rounded-full bg-gray-200 dark:bg-gray-700">
              <div className={`h-full rounded-full ${color}`} style={{ width: `${pct}%` }} />
            </div>
            {ep.resetSec > 0 && <p className="mt-0.5 text-xs text-gray-400">Resets in {ep.resetSec}s</p>}
          </div>
        );
      })}
    </div>
  );
}
