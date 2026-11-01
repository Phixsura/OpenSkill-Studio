"use client";
export function FleetErrTaxPanel({ total, causes, topCause }: { total: number; causes: number; topCause: string | null; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🏷️ Error Taxonomy</h3>
    <div className="text-sm">{total} errors · {causes} root causes</div>
    {topCause && <div className="text-xs text-red-500">Top: {topCause}</div>}
  </div>);
}
