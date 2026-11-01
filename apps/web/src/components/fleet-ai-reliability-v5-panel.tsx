"use client";
export function FleetAiReliabilityV5Panel({ systems, active, uptime, mttr, budget, slis }: { systems: number; active: number; uptime: number; mttr: number; budget: number; slis: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🛡️ AI Reliability v5</h3>
    <div className="text-sm">{active}/{systems} active · {uptime}% · MTTR {mttr}m · {budget}% budget · {slis} SLIs</div>
  </div>);
}
