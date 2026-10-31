"use client";
export function FleetAiGwPanel({ gateways, active, requests, cacheHitRate, tokensSaved }: { gateways: number; active: number; requests: number; cacheHitRate: number; tokensSaved: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🤖 AI Gateway</h3>
    <div className="text-sm">{active}/{gateways} active · {requests.toLocaleString()} req · {cacheHitRate}% cached · {tokensSaved.toLocaleString()} tokens saved</div>
  </div>);
}
