"use client";
export function FleetAiApiGwV2Panel({ gateways, active, routes, requests, authMethods }: { gateways: number; active: number; routes: number; requests: number; authMethods: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🌐 AI API Gateway v2</h3>
    <div className="text-sm">{active}/{gateways} active · {routes} routes · {requests.toLocaleString()} req · {authMethods} auth methods</div>
  </div>);
}
