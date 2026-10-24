"use client";
export function FleetInfraCostV9Panel({ teams, total }: { teams: number; total: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💰 Infra Cost v9</h3>
    <div className="text-sm">{teams} teams · ${total.toLocaleString()}/mo</div>
  </div>);
}
