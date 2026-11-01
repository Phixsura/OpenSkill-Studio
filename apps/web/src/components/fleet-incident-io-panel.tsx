"use client";
export function FleetIncidentIoPanel({ total, active, resolved, avgTtd, avgTtr }: { total: number; active: number; resolved: number; avgTtd: number; avgTtr: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🚨 Incident.io</h3>
    <div className="text-sm">{active} active · {resolved} resolved · TTD {avgTtd}min · TTR {avgTtr}min</div>
  </div>);
}
