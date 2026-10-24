"use client";
export function FleetWorkersAiPanel({ models, active, inferences, avgLatency }: { models: number; active: number; inferences: number; avgLatency: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🤖 Workers AI</h3>
    <div className="text-sm">{active}/{models} active · {inferences.toLocaleString()} inferences · {avgLatency}ms</div>
  </div>);
}
