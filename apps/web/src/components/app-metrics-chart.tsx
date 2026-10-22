"use client";

interface MetricPoint {
  date: string;
  value: number;
}

interface AppMetricsChartProps {
  title: string;
  data: MetricPoint[];
  color?: string;
  unit?: string;
}

export function AppMetricsChart({ title, data, color = "blue", unit = "" }: AppMetricsChartProps) {
  if (data.length === 0) {
    return (
      <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
        <h4 className="mb-2 text-sm font-semibold">{title}</h4>
        <p className="text-center text-sm text-gray-400">No data</p>
      </div>
    );
  }

  const max = Math.max(...data.map(d => d.value), 1);
  const total = data.reduce((s, d) => s + d.value, 0);
  const avg = Math.round(total / data.length);

  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="mb-3 flex items-center justify-between">
        <h4 className="text-sm font-semibold">{title}</h4>
        <span className="text-xs text-gray-500">
          Total: {total.toLocaleString()}{unit} · Avg: {avg.toLocaleString()}{unit}
        </span>
      </div>
      <div className="flex h-24 items-end gap-0.5">
        {data.map((point, i) => (
          <div
            key={i}
            className={`flex-1 rounded-t bg-${color}-500 dark:bg-${color}-600 transition-all`}
            style={{ height: `${(point.value / max) * 100}%`, minHeight: point.value > 0 ? "2px" : "0" }}
            title={`${point.date}: ${point.value}${unit}`}
          />
        ))}
      </div>
      <div className="mt-1 flex justify-between text-xs text-gray-400">
        <span>{data[0]?.date}</span>
        <span>{data[data.length - 1]?.date}</span>
      </div>
    </div>
  );
}
