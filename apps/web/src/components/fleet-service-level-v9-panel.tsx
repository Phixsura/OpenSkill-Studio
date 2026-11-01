"use client";
export function FleetServiceLevelV9Panel({ total, breached }: { total: number; breached: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📊 Service Level v9</h3>
    <div className="text-sm">{total} objectives · {breached} breached</div>
  </div>);
}
