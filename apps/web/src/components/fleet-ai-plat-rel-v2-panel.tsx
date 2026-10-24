"use client";
export function FleetAiPlatRelV2Panel({ systems, active, uptime, incidents, mttr, budget }: { systems: number; active: number; uptime: number; incidents: number; mttr: number; budget: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🛡️ AI Reliability v2</h3>
    <div className="text-sm">{active}/{systems} active · {uptime}% uptime · {incidents} incidents/30d · MTTR {mttr}m · {budget}% budget</div>
  </div>);
}
