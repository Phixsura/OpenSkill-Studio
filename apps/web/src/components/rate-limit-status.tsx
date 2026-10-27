"use client";

interface RateLimitWindow {
  window: string;
  max_requests: number;
  current: number;
  remaining: number;
}

interface RateLimitStatusProps {
  apiKeyPrefix: string;
  appName: string;
  windows: RateLimitWindow[];
  inPenalty: boolean;
  penaltyExpiresAt: string | null;
  totalRequests: number;
  totalBlocked: number;
}

function usagePct(current: number, max: number): number {
  return max > 0 ? Math.round((current / max) * 100) : 0;
}

function barColor(pct: number): string {
  if (pct >= 95) return "bg-red-500";
  if (pct >= 80) return "bg-yellow-500";
  if (pct >= 50) return "bg-blue-500";
  return "bg-green-500";
}

function textColor(pct: number): string {
  if (pct >= 95) return "text-red-600 dark:text-red-400";
  if (pct >= 80) return "text-yellow-600 dark:text-yellow-400";
  return "text-gray-600 dark:text-gray-400";
}

function windowLabel(w: string): string {
  const map: Record<string, string> = { second: "/sec", minute: "/min", hour: "/hr" };
  return map[w] ?? `/${w}`;
}

function formatCountdown(iso: string | null): string {
  if (!iso) return "";
  try {
    const diff = new Date(iso).getTime() - Date.now();
    if (diff <= 0) return "expiring...";
    const secs = Math.ceil(diff / 1000);
    if (secs < 60) return `${secs}s`;
    return `${Math.ceil(secs / 60)}m`;
  } catch {
    return "";
  }
}

export function RateLimitStatus({
  apiKeyPrefix,
  appName,
  windows,
  inPenalty,
  penaltyExpiresAt,
  totalRequests,
  totalBlocked,
}: RateLimitStatusProps) {
  const blockRate =
    totalRequests > 0 ? ((totalBlocked / (totalRequests + totalBlocked)) * 100).toFixed(1) : "0.0";

  return (
    <div className="rounded-lg border border-gray-200 dark:border-gray-700">
      {/* Header */}
      <div className="border-b border-gray-200 px-4 py-3 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="font-semibold">Rate Limits</h3>
            <p className="text-xs text-gray-500">
              <code className="rounded bg-gray-100 px-1 dark:bg-gray-800">{apiKeyPrefix}...</code> •{" "}
              {appName}
            </p>
          </div>
          <div className="text-right text-xs">
            <p className="text-gray-500">{totalRequests.toLocaleString()} requests</p>
            <p className={Number(blockRate) > 5 ? "font-medium text-red-600" : "text-gray-400"}>
              {blockRate}% blocked
            </p>
          </div>
        </div>
      </div>

      {/* Penalty banner */}
      {inPenalty && (
        <div className="flex items-center justify-between bg-red-50 px-4 py-2 dark:bg-red-900/10">
          <span className="text-xs font-medium text-red-700 dark:text-red-400">
            🚫 Rate limit penalty active — all requests blocked
          </span>
          {penaltyExpiresAt && (
            <span className="text-xs text-red-600 dark:text-red-400">
              Expires in {formatCountdown(penaltyExpiresAt)}
            </span>
          )}
        </div>
      )}

      {/* Window bars */}
      <div className="divide-y divide-gray-100 dark:divide-gray-800">
        {windows.map((w) => {
          const pct = usagePct(w.current, w.max_requests);
          return (
            <div key={w.window} className="px-4 py-2.5">
              <div className="flex items-center justify-between text-sm">
                <span className="font-medium">
                  {w.max_requests.toLocaleString()}
                  {windowLabel(w.window)}
                </span>
                <span className={`text-xs ${textColor(pct)}`}>
                  {w.remaining.toLocaleString()} remaining
                </span>
              </div>
              <div className="mt-1 flex items-center gap-2">
                <div className="h-2 flex-1 rounded-full bg-gray-200 dark:bg-gray-700">
                  <div
                    className={`h-full rounded-full transition-all ${barColor(pct)}`}
                    style={{ width: `${Math.min(pct, 100)}%` }}
                  />
                </div>
                <span className={`w-10 text-right text-xs font-medium ${textColor(pct)}`}>
                  {pct}%
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
