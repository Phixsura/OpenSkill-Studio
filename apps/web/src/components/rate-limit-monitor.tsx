"use client";

interface RateLimit { endpoint: string; max: number; remaining: number; window: number; }

export function RateLimitMonitor({ limits }: { limits: RateLimit[] }) {
  if (!limits.length) return <div className="text-center text-gray-400 py-6 text-sm">No rate limits configured</div>;
  return (
    <div className="space-y-2">
      {limits.map(l => {
        const usedPct = Math.round((1 - l.remaining / l.max) * 100);
        const critical = usedPct >= 90;
        return (
          <div key={l.endpoint} className="border dark:border-gray-700 rounded-xl p-3">
            <div className="flex justify-between text-sm mb-1">
              <span className="font-mono text-xs">{l.endpoint}</span>
              <span className={`text-xs font-medium ${critical ? "text-red-500" : "text-gray-500"}`}>
                {l.remaining}/{l.max} remaining ({l.window}s window)
              </span>
            </div>
            <div className="h-2 bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden">
              <div className={`h-full rounded-full transition-all ${critical ? "bg-red-500" : usedPct >= 60 ? "bg-yellow-500" : "bg-green-500"}`}
                style={{ width: `${usedPct}%` }} />
            </div>
          </div>
        );
      })}
    </div>
  );
}
