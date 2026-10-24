"use client";
export function FleetGlobalLbV9Panel({ regions, rps }: { regions: number; rps: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🌍 Global LB v9</h3>
    <div className="text-sm">{regions} regions · {rps.toLocaleString()} rps</div>
  </div>);
}
