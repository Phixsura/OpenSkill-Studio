"use client";
export function FleetAiIncidentPanel({ incidents, open, resolved, mttr, aiAssisted }: { incidents: number; open: number; resolved: number; mttr: number; aiAssisted: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🚨 AI Incident Response</h3>
    <div className="text-sm">{open} open · {resolved} resolved · MTTR {mttr}m · {aiAssisted} AI-assisted</div>
  </div>);
}
