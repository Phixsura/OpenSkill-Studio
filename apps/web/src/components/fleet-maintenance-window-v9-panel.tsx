"use client";
export function FleetMaintenanceWindowV9Panel({ windows, upcoming }: { windows: number; upcoming: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔧 Maintenance Window v9</h3>
    <div className="text-sm">{windows} windows · {upcoming} upcoming</div>
  </div>);
}
