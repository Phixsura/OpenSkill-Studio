"use client";
export function FleetApiUsagePanel({ totalCalls, endpoints, unused, topEndpoint }: { totalCalls: number; endpoints: number; unused: number; topEndpoint: string | null; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📈 API Usage</h3>
    <div className="text-sm">{totalCalls.toLocaleString()} calls · {endpoints} endpoints</div>
    {topEndpoint && <div className="text-xs text-blue-500">Top: {topEndpoint}</div>}
    {unused > 0 && <div className="text-xs text-gray-400">{unused} unused</div>}
  </div>);
}
