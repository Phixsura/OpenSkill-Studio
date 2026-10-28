"use client";

interface ForecastInfo {
  metric: string;
  current: number;
  predicted: number;
  trend: "growing" | "stable" | "declining";
  days_to_limit: number | null;
  growth_rate_per_day: number;
}

interface UsageForecastCardProps {
  forecasts: ForecastInfo[];
  appName: string;
}

const TREND_STYLES: Record<string, { icon: string; color: string }> = {
  growing: { icon: "📈", color: "text-red-600 dark:text-red-400" },
  stable: { icon: "➡️", color: "text-gray-500" },
  declining: { icon: "📉", color: "text-green-600 dark:text-green-400" },
};

function formatNum(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return n.toFixed(0);
}

export default function UsageForecastCard({ forecasts, appName }: UsageForecastCardProps) {
  const atRisk = forecasts.filter((f) => f.days_to_limit !== null && f.days_to_limit < 30).length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Usage Forecast</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {atRisk > 0 && (
          <span className="rounded-full bg-red-100 px-2 py-0.5 text-xs font-medium text-red-700 dark:bg-red-900/30 dark:text-red-400">
            {atRisk} at risk
          </span>
        )}
      </div>

      {forecasts.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No forecasts available</p>
      ) : (
        <div className="space-y-2.5">
          {forecasts.map((f) => {
            const trend = TREND_STYLES[f.trend] ?? TREND_STYLES.stable;
            return (
              <div
                key={f.metric}
                className="rounded-lg border border-gray-100 px-3 py-2 dark:border-gray-800"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span>{trend.icon}</span>
                    <span className="text-sm text-gray-800 dark:text-gray-200">
                      {f.metric.replace(/_/g, " ")}
                    </span>
                  </div>
                  <span className={`text-xs font-medium capitalize ${trend.color}`}>{f.trend}</span>
                </div>
                <div className="mt-1 flex items-center justify-between text-[11px] text-gray-400">
                  <span>
                    Current: {formatNum(f.current)} → Predicted: {formatNum(f.predicted)}
                  </span>
                  {f.days_to_limit !== null && (
                    <span className={f.days_to_limit < 30 ? "font-medium text-red-500" : ""}>
                      {f.days_to_limit}d to limit
                    </span>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
