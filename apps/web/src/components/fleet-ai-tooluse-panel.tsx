"use client";
export function FleetAiToolusePanel({ services, active, toolCalls, tools, successRate }: { services: number; active: number; toolCalls: number; tools: number; successRate: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔧 AI Tool Use</h3>
    <div className="text-sm">{active}/{services} active · {toolCalls.toLocaleString()} calls · {tools} tools · {successRate}%</div>
  </div>);
}
