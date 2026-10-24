"use client";
export function FleetAiRatelimitPanel({ configs, active, throttled, requests }: { configs: number; active: number; throttled: number; requests: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🚦 AI Rate Limit</h3>
    <div className="text-sm">{active}/{configs} active · {throttled.toLocaleString()} throttled / {requests.toLocaleString()} total</div>
  </div>);
}
