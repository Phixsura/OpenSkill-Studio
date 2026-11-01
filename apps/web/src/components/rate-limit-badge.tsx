"use client";

interface RateLimitBadgeProps { remaining: number; limit: number; retryAfterS: number | null; }

export function RateLimitBadge({ remaining, limit, retryAfterS }: RateLimitBadgeProps) {
  const pct = limit > 0 ? Math.round((remaining / limit) * 100) : 0;
  const color = pct > 50 ? "text-green-600" : pct > 20 ? "text-yellow-600" : "text-red-600";
  const bg = pct > 50 ? "bg-green-500" : pct > 20 ? "bg-yellow-500" : "bg-red-500";

  return (
    <div className="flex items-center gap-3 rounded-lg border px-4 py-2.5 dark:border-gray-700">
      <div className="flex-1">
        <div className="flex items-center justify-between text-sm">
          <span className="font-medium">Rate Limit</span>
          <span className={`font-mono ${color}`}>{remaining}/{limit}</span>
        </div>
        <div className="mt-1.5 h-1.5 rounded-full bg-gray-200 dark:bg-gray-700">
          <div className={`h-full rounded-full ${bg} transition-all`} style={{ width: `${pct}%` }} />
        </div>
      </div>
      {retryAfterS != null && (
        <span className="text-xs text-red-500">retry in {retryAfterS}s</span>
      )}
    </div>
  );
}
