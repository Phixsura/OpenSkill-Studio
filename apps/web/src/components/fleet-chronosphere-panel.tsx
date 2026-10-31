"use client";
export function FleetChronospherePanel({ tenants, activeSeries, avgSavings }: { tenants: number; activeSeries: number; avgSavings: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⏱️ Chronosphere</h3>
    <div className="text-sm">{tenants} tenants · {activeSeries.toLocaleString()} series · {avgSavings}% savings</div>
  </div>);
}
