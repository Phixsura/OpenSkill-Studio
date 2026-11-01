"use client";
export function FleetEdgeFunctionV9Panel({ functions, regions }: { functions: number; regions: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⚡ Edge Function v9</h3>
    <div className="text-sm">{functions} functions · {regions} regions</div>
  </div>);
}
