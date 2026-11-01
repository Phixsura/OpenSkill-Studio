"use client";

interface MetricItem { label: string; value: string | number; trend?: "up" | "down" | "flat"; changePct?: number; }

interface MetricsSummaryCardProps { title: string; metrics: MetricItem[]; }

export function MetricsSummaryCard({ title, metrics }: MetricsSummaryCardProps) {
  const trendIcons = { up: "↑", down: "↓", flat: "→" };
  const trendColors = { up: "text-green-600", down: "text-red-600", flat: "text-gray-400" };

  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <h3 className="text-sm font-medium text-gray-500">{title}</h3>
      <div className="mt-3 grid grid-cols-2 gap-4">
        {metrics.map(m => (
          <div key={m.label}>
            <p className="text-2xl font-bold">{typeof m.value === "number" ? m.value.toLocaleString() : m.value}</p>
            <div className="flex items-center gap-1">
              <span className="text-xs text-gray-500">{m.label}</span>
              {m.trend && (
                <span className={`text-xs ${trendColors[m.trend]}`}>
                  {trendIcons[m.trend]} {m.changePct != null ? `${m.changePct}%` : ""}
                </span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
