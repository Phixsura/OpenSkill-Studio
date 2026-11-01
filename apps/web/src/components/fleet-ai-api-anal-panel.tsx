"use client";
export function FleetAiApiAnalPanel({ dashboards, active, endpoints, calls, errorRate }: { dashboards: number; active: number; endpoints: number; calls: number; errorRate: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📊 AI API Analytics</h3>
    <div className="text-sm">{active}/{dashboards} active · {endpoints} endpoints · {calls.toLocaleString()} calls · {errorRate}% errors</div>
  </div>);
}
