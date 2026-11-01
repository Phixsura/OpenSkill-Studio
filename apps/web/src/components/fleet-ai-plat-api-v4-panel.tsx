"use client";
export function FleetAiPlatApiV4Panel({ gateways, active, endpoints, requests, p99, errorRate }: { gateways: number; active: number; endpoints: number; requests: number; p99: number; errorRate: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🌐 AI API v4</h3>
    <div className="text-sm">{active}/{gateways} active · {endpoints} endpoints · {requests.toLocaleString()} req · p99 {p99}ms · {errorRate}% err</div>
  </div>);
}
