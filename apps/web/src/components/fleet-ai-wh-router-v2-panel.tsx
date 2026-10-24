"use client";
export function FleetAiWhRouterV2Panel({ routers, active, webhooks, routed, retrySuccess }: { routers: number; active: number; webhooks: number; routed: number; retrySuccess: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔔 AI Webhook Router v2</h3>
    <div className="text-sm">{active}/{routers} active · {webhooks} webhooks · {routed.toLocaleString()} routed · {retrySuccess}% retry</div>
  </div>);
}
