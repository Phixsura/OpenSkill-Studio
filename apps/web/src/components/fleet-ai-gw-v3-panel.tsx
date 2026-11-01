"use client";
export function FleetAiGwV3Panel({ gateways, active, providers, requests, costSaved }: { gateways: number; active: number; providers: number; requests: number; costSaved: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🌐 AI Gateway v3</h3>
    <div className="text-sm">{active}/{gateways} active · {providers} providers · {requests.toLocaleString()} req · {costSaved}% saved</div>
  </div>);
}
