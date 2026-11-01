"use client";
export function FleetAiRouterPanel({ routers, active, requests, models, fallbackPct }: { routers: number; active: number; requests: number; models: number; fallbackPct: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔀 AI Router</h3>
    <div className="text-sm">{active}/{routers} active · {requests.toLocaleString()} req · {models} models · {fallbackPct}% fallback</div>
  </div>);
}
