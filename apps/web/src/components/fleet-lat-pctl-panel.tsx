"use client";
export function FleetLatPctlPanel({ p50, p95, p99, count }: { p50: number; p95: number; p99: number; count: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📊 Latency Percentiles</h3>
    <div className="grid grid-cols-3 gap-2 text-center text-sm">
      <div><div className="font-bold">{p50}ms</div><div className="text-xs text-gray-400">p50</div></div>
      <div><div className="font-bold">{p95}ms</div><div className="text-xs text-gray-400">p95</div></div>
      <div><div className="font-bold">{p99}ms</div><div className="text-xs text-gray-400">p99</div></div>
    </div>
  </div>);
}
