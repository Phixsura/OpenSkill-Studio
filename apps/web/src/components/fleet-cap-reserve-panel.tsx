"use client";
export function FleetCapReservePanel({ reserved, used, utilPct, waste }: { reserved: number; used: number; utilPct: number; waste: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📦 Capacity Reservations</h3>
    <div className="text-sm">{used}/{reserved} used ({utilPct}%)</div>
    {waste && <span className="text-xs text-yellow-600">💸 Low utilization — consider downsizing</span>}
  </div>);
}
