"use client";
export function FleetMlServingPanel({ models, totalQps, avgP99, staleModels, performant }: { models: number; totalQps: number; avgP99: number; staleModels: number; performant: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🤖 ML Serving</h3>
    <div className="text-sm">{models} models · {totalQps.toLocaleString()} qps · p99 {avgP99}ms</div>
    {staleModels > 0 && <span className="text-xs text-yellow-600">⚠️ {staleModels} stale models</span>}
  </div>);
}
