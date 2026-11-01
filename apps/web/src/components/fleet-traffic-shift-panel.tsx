"use client";
export function FleetTrafficShiftPanel({ targets, primary, primaryPct }: { targets: number; primary: string | null; primaryPct: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔀 Traffic Shift</h3>
    <div className="text-sm">{targets} targets · Primary: {primary ?? "N/A"} ({primaryPct}%)</div>
  </div>);
}
