"use client";
export function FleetAiPlatIncV3Panel({ managers, active, incidents, p1, mttr, postmortems }: { managers: number; active: number; incidents: number; p1: number; mttr: number; postmortems: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🚨 AI Incident v3</h3>
    <div className="text-sm">{active}/{managers} active · {incidents} incidents · {p1} P1 · MTTR {mttr}m · {postmortems} postmortems</div>
  </div>);
}
