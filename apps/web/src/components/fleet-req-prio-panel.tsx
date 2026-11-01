"use client";
export function FleetReqPrioPanel({ total, highPriorityPct }: { total: number; highPriorityPct: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔝 Request Priority</h3>
    <div className="text-sm">{total} requests · {highPriorityPct}% high/critical</div>
  </div>);
}
