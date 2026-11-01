"use client";
export function FleetRateLimitDashboardV9Panel({ apis, throttled }: { apis: number; throttled: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🚧 Rate Limit Dashboard v9</h3>
    <div className="text-sm">{apis} APIs · {throttled} throttled today</div>
  </div>);
}
