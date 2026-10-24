"use client";

interface MetricAggChartProps { count: number; avg: number; min: number; max: number;
  p50: number; p95: number; p99: number; window: string; }

export function MetricAggChart({ count, avg, min, max, p50, p95, p99, window }: MetricAggChartProps) {
  const metrics = [
    { l: "Avg", v: avg }, { l: "Min", v: min }, { l: "Max", v: max },
    { l: "P50", v: p50 }, { l: "P95", v: p95 }, { l: "P99", v: p99 },
  ];
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📊 Metrics ({window})</h3>
        <span className="text-xs text-gray-400">{count} data points</span>
      </div>
      <div className="grid grid-cols-6 gap-px bg-gray-200 dark:bg-gray-700">
        {metrics.map(m => (
          <div key={m.l} className="bg-white dark:bg-gray-900 p-3 text-center">
            <div className="text-sm font-bold">{m.v}</div>
            <div className="text-[10px] text-gray-400">{m.l}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
