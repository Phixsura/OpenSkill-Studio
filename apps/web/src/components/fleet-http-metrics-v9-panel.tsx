"use client";
export function FleetHttpMetricsV9Panel({ endpoints, errorRate }: { endpoints: number; errorRate: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📊 HTTP Metrics v9</h3>
    <div className="text-sm">{endpoints} endpoints · {errorRate}% error rate</div>
  </div>);
}
