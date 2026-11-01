"use client";

interface Bucket { le: number | string; count: number; pct: number; }
interface LatencyHistogramChartProps { histogram: Bucket[]; total: number; avgMs: number;
  p50Ms: number; p99Ms: number; }

export function LatencyHistogramChart({ histogram, total, avgMs, p50Ms, p99Ms }: LatencyHistogramChartProps) {
  const maxCount = Math.max(...histogram.map(b => b.count), 1);
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Latency Distribution</h2>
        <span className="text-xs text-gray-400">{total.toLocaleString()} requests</span>
      </div>
      <div className="grid grid-cols-3 gap-3 text-center">
        <div className="rounded bg-gray-50 p-2 dark:bg-gray-800">
          <p className="text-lg font-bold">{avgMs}ms</p><p className="text-xs text-gray-400">Avg</p>
        </div>
        <div className="rounded bg-gray-50 p-2 dark:bg-gray-800">
          <p className="text-lg font-bold">{p50Ms}ms</p><p className="text-xs text-gray-400">P50</p>
        </div>
        <div className="rounded bg-gray-50 p-2 dark:bg-gray-800">
          <p className="text-lg font-bold">{p99Ms}ms</p><p className="text-xs text-gray-400">P99</p>
        </div>
      </div>
      <div className="flex items-end gap-px" style={{ height: "80px" }}>
        {histogram.filter(b => b.count > 0).map((b, i) => (
          <div key={i} className="flex-1 rounded-t bg-blue-400 dark:bg-blue-600"
            style={{ height: `${(b.count / maxCount) * 100}%` }}
            title={`≤${b.le}ms: ${b.count} (${b.pct}%)`} />
        ))}
      </div>
      <div className="flex justify-between text-[10px] text-gray-400">
        <span>Fast</span><span>Slow</span>
      </div>
    </div>
  );
}
