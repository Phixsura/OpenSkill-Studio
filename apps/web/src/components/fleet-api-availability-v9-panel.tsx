"use client";
export function FleetApiAvailabilityV9Panel({ regions, uptime }: { regions: number; uptime: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🌍 API Availability v9</h3>
    <div className="text-sm">{regions} regions · {uptime}% uptime</div>
  </div>);
}
