"use client";
export function FleetAiFuncCallPanel({ services, active, calls, tools, successRate }: { services: number; active: number; calls: number; tools: number; successRate: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔧 AI Function Calling</h3>
    <div className="text-sm">{active}/{services} active · {calls.toLocaleString()} calls · {tools} tools · {successRate}%</div>
  </div>);
}
