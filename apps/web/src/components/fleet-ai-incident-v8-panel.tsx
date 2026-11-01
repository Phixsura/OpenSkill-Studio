"use client";
export function FleetAiIncidentV8Panel({ managers, active, incidents, mttr, auto }: { managers: number; active: number; incidents: number; mttr: number; auto: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🚨 AI Incident v8</h3>
    <div className="text-sm">{active}/{managers} active · {incidents} incidents · MTTR {mttr}m · {auto} auto-resolved</div>
  </div>);
}
