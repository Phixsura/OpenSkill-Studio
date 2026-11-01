"use client";
export function FleetAiServerlessPanel({ functions, active, invocations, coldStart, cost }: { functions: number; active: number; invocations: number; coldStart: number; cost: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⚡ AI Serverless</h3>
    <div className="text-sm">{active}/{functions} active · {invocations.toLocaleString()} invocations · {coldStart}ms cold · ${cost}/1M</div>
  </div>);
}
