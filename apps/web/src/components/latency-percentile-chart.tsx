"use client";

interface LatencyPercentileChartProps { p50: number; p90: number; p95: number; p99: number;
  avg: number; min: number; max: number; count: number; status: string; }

export function LatencyPercentileChart({ p50, p90, p95, p99, avg, min, max, count, status }: LatencyPercentileChartProps) {
  const bars = [
    { label: "p50", value: p50, color: "bg-green-500" },
    { label: "p90", value: p90, color: "bg-blue-500" },
    { label: "p95", value: p95, color: "bg-yellow-500" },
    { label: "p99", value: p99, color: "bg-red-500" },
  ];
  const maxVal = Math.max(...bars.map(b => b.value), 1);
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold">⏱️ Latency</h3>
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-400">{count.toLocaleString()} samples</span>
          <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
            status === "fast" ? "bg-green-100 text-green-700" :
            status === "ok" ? "bg-yellow-100 text-yellow-700" : "bg-red-100 text-red-700"
          }`}>{status}</span>
        </div>
      </div>
      <div className="space-y-2 mb-4">
        {bars.map(b => (
          <div key={b.label} className="flex items-center gap-3">
            <span className="text-xs font-mono w-8 text-gray-400">{b.label}</span>
            <div className="flex-1 h-5 bg-gray-100 dark:bg-gray-800 rounded">
              <div className={`h-full rounded ${b.color}`}
                   style={{ width: `${(b.value / maxVal) * 100}%` }} />
            </div>
            <span className="text-xs font-mono w-16 text-right">{b.value}ms</span>
          </div>
        ))}
      </div>
      <div className="flex gap-4 text-xs text-gray-400">
        <span>Avg: {avg}ms</span><span>Min: {min}ms</span><span>Max: {max}ms</span>
      </div>
    </div>
  );
}
