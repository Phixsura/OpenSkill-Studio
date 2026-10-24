"use client";
export function FleetApiLatencyTrackerV9Panel({ endpoints, p99 }: { endpoints: number; p99: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⏱️ API Latency Tracker v9</h3>
    <div className="text-sm">{endpoints} endpoints · {p99}ms avg p99</div>
  </div>);
}
