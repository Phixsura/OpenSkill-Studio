"use client";

interface Bucket { timestamp: number; value: number; count: number; }
interface MetricChartCardProps { title: string; buckets: Bucket[]; aggregation: string; unit?: string; }

export function MetricChartCard({ title, buckets, aggregation, unit }: MetricChartCardProps) {
  const maxVal = Math.max(...buckets.map(b => b.value), 1);
  const current = buckets.length > 0 ? buckets[buckets.length - 1].value : 0;
  const prev = buckets.length > 1 ? buckets[buckets.length - 2].value : current;
  const change = prev !== 0 ? Math.round(((current - prev) / prev) * 100) : 0;

  return (
    <div className="rounded-lg border p-4 dark:border-gray-700">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-medium text-gray-500">{title}</h3>
        <span className="rounded bg-gray-100 px-1.5 py-0.5 text-[10px] uppercase dark:bg-gray-800">{aggregation}</span>
      </div>
      <div className="mt-1 flex items-baseline gap-2">
        <span className="text-2xl font-bold">{current}{unit ?? ""}</span>
        {change !== 0 && (
          <span className={`text-xs ${change > 0 ? "text-green-500" : "text-red-500"}`}>
            {change > 0 ? "↑" : "↓"}{Math.abs(change)}%
          </span>
        )}
      </div>
      <div className="mt-3 flex items-end gap-px" style={{ height: "40px" }}>
        {buckets.map((b, i) => (
          <div key={i} className="flex-1 rounded-t bg-blue-400 dark:bg-blue-600"
            style={{ height: `${(b.value / maxVal) * 100}%`, opacity: 0.5 + (i / buckets.length) * 0.5 }} />
        ))}
      </div>
    </div>
  );
}
