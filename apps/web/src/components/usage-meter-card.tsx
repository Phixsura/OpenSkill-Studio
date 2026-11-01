"use client";

interface MetricUsage {
  metric: string;
  used: number;
  limit: number | null;
  remaining: number | null;
  usage_pct: number | null;
  exceeded: boolean;
  window: "hourly" | "daily" | "monthly";
}

interface UsageMeterCardProps {
  metrics: MetricUsage[];
  appName: string;
}

function formatQuantity(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return n.toFixed(0);
}

function UsageBar({ pct, exceeded }: { pct: number; exceeded: boolean }) {
  const clamped = Math.min(pct, 100);
  const color = exceeded ? "bg-red-500" : pct >= 80 ? "bg-yellow-500" : "bg-green-500";
  return (
    <div className="h-2 w-full rounded-full bg-gray-200 dark:bg-gray-700">
      <div
        className={`h-2 rounded-full transition-all ${color}`}
        style={{ width: `${clamped}%` }}
      />
    </div>
  );
}

const WINDOW_LABELS: Record<string, string> = {
  hourly: "this hour",
  daily: "today",
  monthly: "this month",
};

export default function UsageMeterCard({ metrics, appName }: UsageMeterCardProps) {
  const exceededCount = metrics.filter((m) => m.exceeded).length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      {/* Header */}
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Usage Meter</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {exceededCount > 0 ? (
          <span className="rounded-full bg-red-100 px-2 py-0.5 text-xs font-medium text-red-700 dark:bg-red-900/30 dark:text-red-400">
            {exceededCount} over quota
          </span>
        ) : (
          <span className="rounded-full bg-green-100 px-2 py-0.5 text-xs font-medium text-green-700 dark:bg-green-900/30 dark:text-green-400">
            Within limits
          </span>
        )}
      </div>

      {/* Metric rows */}
      {metrics.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No metrics tracked</p>
      ) : (
        <div className="space-y-4">
          {metrics.map((m) => (
            <div key={m.metric}>
              <div className="mb-1 flex items-center justify-between">
                <span className="text-sm font-medium text-gray-800 dark:text-gray-200">
                  {m.metric.replace(/_/g, " ")}
                </span>
                <span className="text-xs text-gray-500 dark:text-gray-400">
                  {WINDOW_LABELS[m.window] ?? m.window}
                </span>
              </div>
              {m.limit !== null ? (
                <>
                  <UsageBar pct={m.usage_pct ?? 0} exceeded={m.exceeded} />
                  <div className="mt-1 flex items-center justify-between">
                    <span className="text-xs text-gray-500">
                      {formatQuantity(m.used)} / {formatQuantity(m.limit)}
                    </span>
                    <span
                      className={`text-xs font-medium ${
                        m.exceeded ? "text-red-600 dark:text-red-400" : "text-gray-500"
                      }`}
                    >
                      {m.exceeded
                        ? "Quota exceeded"
                        : `${m.remaining !== null ? formatQuantity(m.remaining) : "—"} remaining`}
                    </span>
                  </div>
                </>
              ) : (
                <div className="flex items-center justify-between">
                  <span className="text-xs text-gray-500">{formatQuantity(m.used)} used</span>
                  <span className="text-xs text-gray-400">No limit</span>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
