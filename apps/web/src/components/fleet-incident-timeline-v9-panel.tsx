"use client";
export function FleetIncidentTimelineV9Panel({ incidents, resolved }: { incidents: number; resolved: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🚨 Incident Timeline v9</h3>
    <div className="text-sm">{incidents} incidents · {resolved} resolved</div>
  </div>);
}
