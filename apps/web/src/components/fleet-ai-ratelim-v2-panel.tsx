"use client";
export function FleetAiRatelimV2Panel({ limiters, active, throttled, total, throttlePct }: { limiters: number; active: number; throttled: number; total: number; throttlePct: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🚦 AI Rate Limiter v2</h3>
    <div className="text-sm">{active}/{limiters} active · {throttled.toLocaleString()} throttled · {total.toLocaleString()} total · {throttlePct}%</div>
  </div>);
}
