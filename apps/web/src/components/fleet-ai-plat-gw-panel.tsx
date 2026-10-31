"use client";
export function FleetAiPlatGwPanel({ gateways, active, routes, requests, p99 }: { gateways: number; active: number; routes: number; requests: number; p99: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🌐 AI Platform Gateway</h3>
    <div className="text-sm">{active}/{gateways} active · {routes} routes · {requests.toLocaleString()} req · p99 {p99}ms</div>
  </div>);
}
