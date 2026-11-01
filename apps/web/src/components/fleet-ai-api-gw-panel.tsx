"use client";
export function FleetAiApiGwPanel({ gateways, active, providers, requests, cost }: { gateways: number; active: number; providers: number; requests: number; cost: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🚪 AI API Gateway</h3>
    <div className="text-sm">{active}/{gateways} active · {providers} providers · {requests.toLocaleString()} req · ${cost.toLocaleString()}</div>
  </div>);
}
