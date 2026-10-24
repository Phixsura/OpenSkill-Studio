"use client";
export function FleetLatencyBudgetV9Panel({ services, p99 }: { services: number; p99: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⏱️ Latency Budget v9</h3>
    <div className="text-sm">{services} services · {p99}ms avg p99</div>
  </div>);
}
