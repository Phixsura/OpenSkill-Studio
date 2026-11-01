"use client";
export function FleetObsCostPanel({ totalMonthly, expensive }: { totalMonthly: number; expensive: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💸 Observability Cost</h3>
    <div className="text-sm">${totalMonthly.toLocaleString()}/mo</div>
    {expensive && <span className="text-xs text-yellow-600">⚠️ High observability spend</span>}
  </div>);
}
