"use client";
export function FleetApiThrottleV9Panel({ consumers, throttled }: { consumers: number; throttled: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🚧 API Throttle v9</h3>
    <div className="text-sm">{consumers} consumers · {throttled} throttled</div>
  </div>);
}
