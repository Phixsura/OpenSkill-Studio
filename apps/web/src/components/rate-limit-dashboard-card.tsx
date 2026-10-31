"use client";

interface RateLimitInfo {
  key: string;
  count: number;
  limit: number;
  remaining: number;
  window_seconds: number;
  reset_in_seconds: number;
  blocked: boolean;
}

interface RateLimitDashboardCardProps {
  limits: RateLimitInfo[];
  appName: string;
}

function UsageBar({ count, limit }: { count: number; limit: number }) {
  const pct = limit > 0 ? Math.min((count / limit) * 100, 100) : 0;
  const color = pct >= 100 ? "bg-red-500" : pct >= 80 ? "bg-yellow-500" : "bg-green-500";
  return (
    <div className="h-1.5 w-full rounded-full bg-gray-200 dark:bg-gray-700">
      <div className={`h-1.5 rounded-full ${color}`} style={{ width: `${pct}%` }} />
    </div>
  );
}

export default function RateLimitDashboardCard({ limits, appName }: RateLimitDashboardCardProps) {
  const blockedCount = limits.filter((l) => l.blocked).length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Rate Limits</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {blockedCount > 0 ? (
          <span className="rounded-full bg-red-100 px-2 py-0.5 text-xs font-medium text-red-700 dark:bg-red-900/30 dark:text-red-400">
            {blockedCount} throttled
          </span>
        ) : (
          <span className="rounded-full bg-green-100 px-2 py-0.5 text-xs font-medium text-green-700 dark:bg-green-900/30 dark:text-green-400">
            All clear
          </span>
        )}
      </div>

      {limits.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No rate limits tracked</p>
      ) : (
        <div className="space-y-3">
          {limits.map((l) => (
            <div
              key={l.key}
              className="rounded-lg border border-gray-100 px-3 py-2.5 dark:border-gray-800"
            >
              <div className="mb-1.5 flex items-center justify-between">
                <span className="font-mono text-sm text-gray-800 dark:text-gray-200">{l.key}</span>
                <span className="text-[11px] text-gray-400">{l.window_seconds}s window</span>
              </div>
              <UsageBar count={l.count} limit={l.limit} />
              <div className="mt-1 flex items-center justify-between text-[11px]">
                <span className="text-gray-500">
                  {l.count} / {l.limit} requests
                </span>
                {l.blocked ? (
                  <span className="font-medium text-red-600 dark:text-red-400">
                    Resets in {l.reset_in_seconds}s
                  </span>
                ) : (
                  <span className="text-gray-400">{l.remaining} remaining</span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
