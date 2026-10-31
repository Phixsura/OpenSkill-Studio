"use client";
export function FleetApiAnalyticsPanel({ totalCalls, uniqueConsumers, avgCallsPerConsumer, topEndpoint }: { totalCalls: number; uniqueConsumers: number; avgCallsPerConsumer: number; topEndpoint: string; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📊 API Analytics</h3>
    <div className="text-sm">{totalCalls.toLocaleString()} calls · {uniqueConsumers} consumers · {avgCallsPerConsumer}/consumer</div>
    <div className="text-xs text-blue-500">Top: {topEndpoint}</div>
  </div>);
}
