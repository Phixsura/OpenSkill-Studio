"use client";

interface LatencyDistributionCardProps { p50: number; p90: number; p95: number; p99: number; avg: number; targetP99?: number; }

export function LatencyDistributionCard({ p50, p90, p95, p99, avg, targetP99 }: LatencyDistributionCardProps) {
  const withinBudget = targetP99 ? p99 <= targetP99 : true;
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold">Latency Distribution</h3>
        {targetP99 && (
          <span className={`text-xs font-medium ${withinBudget ? "text-green-600" : "text-red-600"}`}>
            {withinBudget ? "✅" : "⚠️"} Target: {targetP99}ms
          </span>
        )}
      </div>
      <div className="mt-3 grid grid-cols-5 gap-2 text-center">
        {[{ label: "AVG", value: avg }, { label: "P50", value: p50 }, { label: "P90", value: p90 },
          { label: "P95", value: p95 }, { label: "P99", value: p99 }].map(m => (
          <div key={m.label}>
            <p className={`text-lg font-bold ${m.label === "P99" && targetP99 && m.value > targetP99 ? "text-red-600" : ""}`}>{m.value}</p>
            <p className="text-xs text-gray-400">{m.label}</p>
          </div>
        ))}
      </div>
      <p className="mt-2 text-center text-xs text-gray-400">milliseconds</p>
    </div>
  );
}
