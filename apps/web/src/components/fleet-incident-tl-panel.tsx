"use client";
export function FleetIncidentTlPanel({ total, sev1, sev2, resolved, open }: { total: number; sev1: number; sev2: number; resolved: number; open: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🚨 Incident Timeline</h3>
    <div className="text-sm">{total} incidents · {sev1} SEV1 · {sev2} SEV2</div>
    <div className="text-xs text-gray-400">{resolved} resolved · {open} open</div>
  </div>);
}
