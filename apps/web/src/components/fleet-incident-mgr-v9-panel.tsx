"use client";
export function FleetIncidentMgrV9Panel({ open, resolved }: { open: number; resolved: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🚨 Incident Manager v9</h3>
    <div className="text-sm">{open} open · {resolved} resolved</div>
  </div>);
}
