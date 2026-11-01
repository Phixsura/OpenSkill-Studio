"use client";
export function FleetRateLimiterV9Panel({ endpoints, throttlePct }: { endpoints: number; throttlePct: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🚧 Rate Limiter v9</h3>
    <div className="text-sm">{endpoints} endpoints · {throttlePct}% throttled</div>
  </div>);
}
