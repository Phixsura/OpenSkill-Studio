"use client";
export function FleetAiToolCallPanel({ services, active, tools, calls, latency }: { services: number; active: number; tools: number; calls: number; latency: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔧 AI Tool Calling</h3>
    <div className="text-sm">{active}/{services} active · {tools} tools · {calls.toLocaleString()} calls · {latency}ms</div>
  </div>);
}
