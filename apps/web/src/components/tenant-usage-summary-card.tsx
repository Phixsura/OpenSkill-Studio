"use client";

interface MetricInfo {
  metric: string;
  current: number;
  limit: number;
  usage_pct: number;
  growth_pct: number;
}

interface TenantUsageSummaryCardProps {
  metrics: MetricInfo[];
  health: "healthy" | "warning" | "critical";
  totalCostDollars: number;
  appName: string;
}

const HEALTH_STYLES: Record<string, { bg: string; text: string; label: string }> = {
  healthy: {
    bg: "bg-green-100 dark:bg-green-900/30",
    text: "text-green-700 dark:text-green-400",
    label: "Healthy",
  },
  warning: {
    bg: "bg-yellow-100 dark:bg-yellow-900/30",
    text: "text-yellow-700 dark:text-yellow-400",
    label: "Warning",
  },
  critical: {
    bg: "bg-red-100 dark:bg-red-900/30",
    text: "text-red-700 dark:text-red-400",
    label: "Critical",
  },
};

function formatNum(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return n.toFixed(0);
}

export default function TenantUsageSummaryCard({
  metrics,
  health,
  totalCostDollars,
  appName,
}: TenantUsageSummaryCardProps) {
  const hs = HEALTH_STYLES[health] ?? HEALTH_STYLES.healthy;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Usage Summary</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="flex items-center gap-2">
          <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${hs.bg} ${hs.text}`}>
            {hs.label}
          </span>
          <span className="text-xs font-medium text-gray-800 dark:text-gray-200">
            ${totalCostDollars.toFixed(2)}
          </span>
        </div>
      </div>

      {metrics.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No usage data</p>
      ) : (
        <div className="space-y-2.5">
          {metrics.map((m) => {
            const barColor =
              m.usage_pct >= 95
                ? "bg-red-500"
                : m.usage_pct >= 80
                  ? "bg-yellow-500"
                  : "bg-green-500";
            return (
              <div key={m.metric}>
                <div className="mb-0.5 flex items-center justify-between text-xs">
                  <span className="text-gray-700 dark:text-gray-300">
                    {m.metric.replace(/_/g, " ")}
                  </span>
                  <div className="flex items-center gap-2">
                    <span className="text-gray-500">
                      {formatNum(m.current)}/{formatNum(m.limit)}
                    </span>
                    {m.growth_pct !== 0 && (
                      <span
                        className={`text-[10px] ${m.growth_pct > 0 ? "text-red-500" : "text-green-500"}`}
                      >
                        {m.growth_pct > 0 ? "↑" : "↓"}
                        {Math.abs(m.growth_pct)}%
                      </span>
                    )}
                  </div>
                </div>
                <div className="h-1.5 rounded-full bg-gray-200 dark:bg-gray-700">
                  <div
                    className={`h-1.5 rounded-full ${barColor}`}
                    style={{ width: `${Math.min(m.usage_pct, 100)}%` }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
