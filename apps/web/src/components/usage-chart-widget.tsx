"use client";

interface UsageChartWidgetProps { labels: string[]; values: number[]; metric: string;
  total: number; average: number; peak: number; trend: string; }

export function UsageChartWidget({ labels, values, metric, total, average, peak, trend }: UsageChartWidgetProps) {
  const maxVal = Math.max(...values, 1);
  const trendIcon = trend === "up" ? "📈" : trend === "down" ? "📉" : "➡️";
  return (
    <div className="rounded-xl border p-4 dark:border-gray-700">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-semibold capitalize">{metric.replace("_", " ")}</h3>
        <div className="flex items-center gap-2 text-xs text-gray-400">
          <span>{trendIcon}</span>
          <span>Total: {total.toLocaleString()}</span>
          <span>Avg: {average.toLocaleString()}</span>
        </div>
      </div>
      <div className="flex items-end gap-px h-20">
        {values.map((v, i) => (
          <div key={i} className="flex-1" title={`${labels[i]}: ${v.toLocaleString()}`}>
            <div className="w-full rounded-t bg-blue-500 transition-all"
              style={{ height: `${(v / maxVal) * 100}%`, minHeight: v > 0 ? 3 : 0 }} />
          </div>
        ))}
      </div>
      {labels.length > 0 && (
        <div className="flex justify-between mt-1 text-xs text-gray-400">
          <span>{labels[0]}</span>
          <span>{labels[labels.length - 1]}</span>
        </div>
      )}
    </div>
  );
}
