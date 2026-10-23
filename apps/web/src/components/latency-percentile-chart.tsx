"use client";

interface LatencyPercentileChartProps { p50: number; p90: number; p95: number;
  p99: number; avg: number; max: number; count: number; sloMet: boolean; }

export function LatencyPercentileChart({ p50, p90, p95, p99, avg, max, count, sloMet }: LatencyPercentileChartProps) {
  const maxVal = Math.max(p99, max, 1);
  const bars = [
    { label: "p50", value: p50 }, { label: "p90", value: p90 },
    { label: "p95", value: p95 }, { label: "p99", value: p99 },
  ];
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">⏱️ Latency Percentiles</h3>
        <div className="flex gap-2 text-xs">
          <span className="text-gray-400">{count} samples · avg {avg}ms</span>
          <span className={sloMet ? "text-green-600" : "text-red-500"}>{sloMet ? "✅ SLO met" : "⚠ SLO breach"}</span>
        </div>
      </div>
      <div className="p-4 space-y-2">
        {bars.map(b => (
          <div key={b.label}>
            <div className="flex justify-between text-xs mb-0.5">
              <span className="font-mono font-medium">{b.label}</span>
              <span className="text-gray-400">{b.value}ms</span>
            </div>
            <div className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-full">
              <div className={`h-full rounded-full ${b.label === "p99" && !sloMet ? "bg-red-500" : "bg-blue-500"}`}
                style={{ width: `${(b.value / maxVal) * 100}%` }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
