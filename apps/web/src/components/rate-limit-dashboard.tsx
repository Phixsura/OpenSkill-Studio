"use client";

interface RateLimitEntry { key: string; limit: number; remaining: number; blocked: number; usagePct: number; }
interface RateLimitDashboardProps { entries: RateLimitEntry[]; }

export function RateLimitDashboard({ entries }: RateLimitDashboardProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <h3 className="font-semibold mb-3">⚡ Rate Limits</h3>
      <div className="space-y-3">
        {entries.map(e => (
          <div key={e.key} className="space-y-1">
            <div className="flex justify-between text-sm">
              <span className="font-mono text-xs">{e.key}</span>
              <span className="text-gray-400">{e.remaining}/{e.limit} remaining</span>
            </div>
            <div className="h-2 bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden">
              <div className={`h-full rounded-full transition-all ${e.usagePct > 90 ? "bg-red-500" : e.usagePct > 70 ? "bg-yellow-500" : "bg-green-500"}`}
                   style={{ width: `${e.usagePct}%` }} />
            </div>
            {e.blocked > 0 && (
              <p className="text-xs text-red-500">{e.blocked} requests blocked</p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
