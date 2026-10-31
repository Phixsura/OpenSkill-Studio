"use client";
export function FleetApiIncidentDashboardV9Panel({ incidents, open }: { incidents: number; open: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🚨 Incident Dashboard v9</h3>
    <div className="text-sm">{incidents} incidents · {open} open</div>
  </div>);
}
