"use client";
export function FleetApiAnalyticsV9Panel({ endpoints, calls }: { endpoints: number; calls: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📊 API Analytics v9</h3>
    <div className="text-sm">{endpoints} endpoints · {calls.toLocaleString()} calls/day</div>
  </div>);
}
