"use client";
export function FleetApiRateControlV9Panel({ policies, throttled }: { policies: number; throttled: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🚧 API Rate Control v9</h3>
    <div className="text-sm">{policies} policies · {throttled} throttled</div>
  </div>);
}
