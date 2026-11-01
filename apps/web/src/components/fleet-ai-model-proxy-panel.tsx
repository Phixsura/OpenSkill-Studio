"use client";
export function FleetAiModelProxyPanel({ proxies, active, requests, models, overhead }: { proxies: number; active: number; requests: number; models: number; overhead: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔀 AI Model Proxy</h3>
    <div className="text-sm">{active}/{proxies} active · {requests.toLocaleString()} req · {models} models · {overhead}ms overhead</div>
  </div>);
}
