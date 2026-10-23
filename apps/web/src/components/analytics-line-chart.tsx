"use client";

interface AnalyticsLineChartProps { labels: string[]; values: number[]; metric: string;
  total: number; average: number; peak: number; trend: string; }

export function AnalyticsLineChart({ labels, values, metric, total, average, peak, trend }: AnalyticsLineChartProps) {
  const maxVal = Math.max(...values, 1);
  const trendIcon = trend === "up" ? "📈" : trend === "down" ? "📉" : "➡️";

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold capitalize">{metric}</h3>
        <div className="flex items-center gap-2 text-xs text-gray-400">
          <span>{trendIcon}</span>
          <span>Total: {total.toLocaleString()}</span>
          <span>Avg: {average}</span>
          <span>Peak: {peak}</span>
        </div>
      </div>
      <div className="flex items-end gap-px h-24">
        {values.map((v, i) => (
          <div key={i} className="flex-1 flex flex-col items-center" title={`${labels[i]}: ${v}`}>
            <div className="w-full rounded-t bg-blue-500 transition-all"
              style={{ height: `${(v / maxVal) * 100}%`, minHeight: v > 0 ? 4 : 0 }} />
          </div>
        ))}
      </div>
      <div className="flex justify-between text-xs text-gray-400">
        <span>{labels[0]}</span>
        <span>{labels[labels.length - 1]}</span>
      </div>
    </div>
  );
}
