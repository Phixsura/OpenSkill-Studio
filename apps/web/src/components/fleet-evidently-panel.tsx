"use client";
export function FleetEvidentlyPanel({ dashboards, active, reports, driftAlerts }: { dashboards: number; active: number; reports: number; driftAlerts: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📊 Evidently</h3>
    <div className="text-sm">{active}/{dashboards} active · {reports} reports · {driftAlerts} drift alerts</div>
  </div>);
}
