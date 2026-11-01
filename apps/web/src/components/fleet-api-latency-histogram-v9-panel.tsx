"use client";
export function FleetApiLatencyHistogramV9Panel({ endpoints, p99 }: { endpoints: number; p99: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📊 Latency Histogram v9</h3>
    <div className="text-sm">{endpoints} endpoints · {p99}% under 100ms</div>
  </div>);
}
