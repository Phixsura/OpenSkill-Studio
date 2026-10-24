"use client";

interface PerformanceSummaryCardProps {
  count: number;
  avgMs: number;
  p50Ms: number;
  p95Ms: number;
  p99Ms: number;
}

export function PerformanceSummaryCard({ count, avgMs, p50Ms, p95Ms, p99Ms }: PerformanceSummaryCardProps) {
  const metrics = [
    { label: "Avg", value: avgMs, unit: "ms" },
    { label: "P50", value: p50Ms, unit: "ms" },
    { label: "P95", value: p95Ms, unit: "ms" },
    { label: "P99", value: p99Ms, unit: "ms" },
  ];

  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="mb-3 flex items-center justify-between">
        <h4 className="font-semibold">⚡ Performance</h4>
        <span className="text-xs text-gray-500">{count.toLocaleString()} executions</span>
      </div>
      {count === 0 ? (
        <p className="text-sm text-gray-400">No execution data</p>
      ) : (
        <div className="grid grid-cols-4 gap-2 text-center">
          {metrics.map(m => (
            <div key={m.label}>
              <p className="text-lg font-bold">{m.value}</p>
              <p className="text-xs text-gray-500">{m.label} ({m.unit})</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
