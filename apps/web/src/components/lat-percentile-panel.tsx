"use client";
interface LatPercentilePanelProps { samples: number; p50: number; p90: number; p95: number; p99: number; avg: number; }
export function LatPercentilePanel({ samples, p50, p90, p95, p99, avg }: LatPercentilePanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📊 Latency Percentiles</h3>
        <span className="text-xs text-gray-400">{samples.toLocaleString()} samples · avg {avg}ms</span>
      </div>
      <div className="grid grid-cols-4 gap-2 p-4 text-center text-xs">
        <div><span className="text-gray-400">P50</span><div className="font-bold text-lg">{p50}ms</div></div>
        <div><span className="text-gray-400">P90</span><div className="font-bold text-lg">{p90}ms</div></div>
        <div><span className="text-gray-400">P95</span><div className="font-bold text-lg">{p95}ms</div></div>
        <div><span className="text-gray-400">P99</span><div className="font-bold text-lg">{p99}ms</div></div>
      </div>
    </div>
  );
}
