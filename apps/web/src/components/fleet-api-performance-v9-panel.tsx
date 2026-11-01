"use client";
export function FleetApiPerformanceV9Panel({ endpoints, avgMs }: { endpoints: number; avgMs: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🏎️ API Performance v9</h3>
    <div className="text-sm">{endpoints} endpoints · {avgMs}ms avg</div>
  </div>);
}
