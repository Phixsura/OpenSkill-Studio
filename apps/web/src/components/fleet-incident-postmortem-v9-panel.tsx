"use client";
export function FleetIncidentPostmortemV9Panel({ total, resolved }: { total: number; resolved: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📝 Postmortem v9</h3>
    <div className="text-sm">{total} postmortems · {resolved} actions resolved</div>
  </div>);
}
