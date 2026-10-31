"use client";
export function FleetAiModelRouterV3Panel({ routers, active, models, routes, optimal }: { routers: number; active: number; models: number; routes: number; optimal: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔀 AI Model Router v3</h3>
    <div className="text-sm">{active}/{routers} active · {models} models · {routes.toLocaleString()} routes · {optimal}% optimal</div>
  </div>);
}
