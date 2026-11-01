"use client";
export function FleetAiReqRouterPanel({ routers, active, routes, strategies, optimalPct }: { routers: number; active: number; routes: number; strategies: string[]; optimalPct: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔀 AI Request Router</h3>
    <div className="text-sm">{active}/{routers} active · {routes.toLocaleString()} routes · {strategies.join(", ")} · {optimalPct}% optimal</div>
  </div>);
}
