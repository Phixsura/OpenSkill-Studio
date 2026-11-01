"use client";
export function FleetCrossRegionV9Panel({ regions, lag }: { regions: number; lag: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🌎 Cross-Region v9</h3>
    <div className="text-sm">{regions} regions · {lag}ms lag</div>
  </div>);
}
